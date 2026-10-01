"""Navigation requests that allow the weighing screen to commit current edits."""

from ui.report_state import app_state


def sync_navigation() -> None:
    selection = app_state.get("seg_nav")
    if selection not in (0, 1, 2, 3):
        return
    if app_state.get("step_index") == 2 and selection == 3:
        # Render Weighing once more to consume the latest editor/widget values.
        app_state["_summary_navigation_requested"] = True
        return
    app_state.pop("_summary_navigation_requested", None)
    app_state["step_index"] = selection
