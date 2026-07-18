from ooklept.base import Element as el

def render_medical_dashboard() -> str:
    # Outer container for the page
    with el("div").class_("dashboard-wrapper") as root:

        # Header
        with el("header"):
            el("h1").text("Doctor's CMS Preparation Tracker")
            el("p").text("Stay organized, stay clinical.")

        # Main Grid Layout
        with el("main").class_("grid-layout"):

            # Sidebar: Task List
            with el("section").class_("sidebar"):
                el("h3").text("To-Do List")
                with el("ul"):
                    el("li").text("Review NTEP 2026 Guidelines")
                    el("li").text("Practice Biostatistics MCQs")
                    el("li").text("Update Immunization Game logic")

            # Content Area: Dynamic Form
            with el("section").class_("main-content"):
                el("h2").text("Add Patient Case")
                with el("form").attr(action="/log-case", method="POST"):
                    # Using required=True (Boolean property)
                    el("input").attr(
                        type="text",
                        placeholder="Patient ID",
                        required=True
                    )
                    # Using disabled=True (Boolean property)
                    el("input").attr(
                        type="date",
                        disabled=False
                    )
                    el("button").attr(type="submit").text("Save Record")

        # Footer
        with el("footer"):
            el("small").text("UPSC CMS 2026 Edition | Status: Active")

    return str(root)

# Usage
if __name__ == "__main__":
    with open("testy.html", "w") as f:
        f.write(render_medical_dashboard())
