// @@TODO: add tests.
import React, { useEffect, useState } from "react";
import { getConfig } from "@edx/frontend-platform";
import { getAuthenticatedHttpClient } from "@edx/frontend-platform/auth";
import { Icon, IconButton } from "@openedx/paragon";
import { Star, StarOutline } from "@openedx/paragon/icons";

// @@TODO: Verify the actual prop name passed by
// org.openedx.frontend.learning.sequence_container.v1. It might be `unitId`,
// `usageKey`, or nested inside a `unit` object. For this POC we accept any of
// the obvious aliases.
const extractUsageKey = (props) =>
  props.usageKey ||
  props.unitId ||
  props.unit?.id ||
  props.unit?.usageKey ||
  null;

const apiUrl = () =>
  `${getConfig().LMS_BASE_URL}/sample-plugin/api/v1/unit-rating/`;

const RateThisContent = (props) => {
  const usageKey = extractUsageKey(props);
  const [stars, setStars] = useState(0); // 0 = not yet rated
  const [existingId, setExistingId] = useState(null);
  const [saving, setSaving] = useState(false);

  // Fetch the caller's existing rating for this unit (if any) on mount.
  useEffect(() => {
    if (!usageKey) return;
    let cancelled = false;
    (async () => {
      try {
        const client = getAuthenticatedHttpClient();
        const { data } = await client.get(apiUrl(), {
          params: { usage_key: usageKey },
        });
        if (cancelled) return;
        const existing = (data?.results || [])[0];
        if (existing) {
          setStars(existing.stars);
          setExistingId(existing.id);
        }
      } catch (e) {
        // @@TODO: surface to user via toast. POC: console only.
        console.error("RateThisContent: failed to fetch existing rating", e);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [usageKey]);

  if (!usageKey) {
    // No usage key in slot props -- nothing to rate.
    // @@TODO: remove once we've confirmed the slot prop shape.
    return null;
  }

  const handleClick = async (value) => {
    const previousStars = stars;
    const previousId = existingId;
    // Optimistic update.
    setStars(value);
    setSaving(true);
    try {
      const client = getAuthenticatedHttpClient();
      if (previousId) {
        await client.patch(`${apiUrl()}${previousId}/`, { stars: value });
      } else {
        const { data } = await client.post(apiUrl(), {
          usage_key: usageKey,
          stars: value,
        });
        setExistingId(data.id);
      }
    } catch (e) {
      console.error("RateThisContent: failed to save rating", e);
      // Revert on failure.
      setStars(previousStars);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="d-flex align-items-center my-3 p-3 border rounded">
      <span className="me-3 fw-bold">Rate this content:</span>
      {[1, 2, 3, 4, 5].map((value) => (
        <IconButton
          key={value}
          src={value <= stars ? Star : StarOutline}
          iconAs={Icon}
          alt={`Rate ${value} stars`}
          onClick={() => handleClick(value)}
          disabled={saving}
          variant="primary"
        />
      ))}
    </div>
  );
};

export default RateThisContent;
