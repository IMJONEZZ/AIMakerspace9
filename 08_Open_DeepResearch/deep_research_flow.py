"""Main Kitaru implementation for the Deep Research agent."""
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import kitaru
from kitaru import flow
from checkpoints import (
    clarify_with_user,
    write_research_brief,
    run_research_supervisor,
    final_report_generation,
    save_report_markdown,
)

# Commenting out max_iterations.
#MAX_ITERATIONS = 25 # Using the same MAX_ITERATIONS as Chris did in reference deep_research_flow.py

# Asks the user clarifying questions if the query is vague.

# deep_research_flow defines the pipeline and tells Kitaru
# the order that different checkpoints should be called in. 
# Return the final saved report.
@flow
def deep_research_flow(user_query: str) -> str:
    """Defines the pipeline that the agent should take. Runs the whole deep research process, starting
    with clarification, then brief, then supervisor, then final report. 
    
        Args:
            user_query: The user query
        
        Returns:
            saved_report: the final, saved report.

    """
    # First, clarify input with the user
    clarified_query = clarify_with_user.submit(user_query).load()

    # After clarification, pass the clarified_query to write_research_brief
    brief = write_research_brief.submit(clarified_query).load()

    # After we've written the brief, pass it to the research supervisor
    notes = run_research_supervisor.submit(brief).load()

    # Now, we have notes on the research topic. We can compile the final report.
    final_report = final_report_generation.submit(brief, notes).load()

    # Finally, save the finalized report as a markdown file (save to disk).
    saved_report = save_report_markdown.submit(final_report).load()

    return saved_report


if __name__ == "__main__":
    import sys
    query = sys.argv[1]
    handle = deep_research_flow.run(query)
    result = handle.wait()
    print(result)

