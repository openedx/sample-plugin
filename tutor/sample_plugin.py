from tutormfe.hooks import PLUGIN_SLOTS

PLUGIN_SLOTS.add_items([
    # Replace the course_list
    (
        "learner-dashboard",
        "custom_course_list",
        """
        {
          op: PLUGIN_OPERATIONS.Insert,
          type: DIRECT_PLUGIN,
          priority: 50,
          RenderWidget:
        }"""
    ),
])
