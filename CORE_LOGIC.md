# ADHD Task Board: Core Logic and Implementation

## Reason and Logic

The ADHD Task Board is a purpose-built physiological and cognitive externalisation of the executive function, designed to bypass the traditional "wall of awful" associated with digital planners [cite: 2026-04-25]. By utilising a high-contrast, stripped-back kiosk interface, the app combats time blindness through a visual progress bar system that converts abstract deadlines into tangible, shrinking geometric areas [cite: 2026-04-25]. The logic operates on the biological reality of the nervous system, avoiding toxic positivity in favour of raw, practical feedback and physiological pacing [cite: 2026-04-25]. The system prioritises a "top-five" hierarchy to prevent choice paralysis, ensuring that only the most critical objectives occupy the primary visual field, while secondary tasks are relegated to a sub-queue to minimise cognitive load [cite: 2026-04-25].

The underlying mechanics leverage predictive coding and the Hermetic law of cause and effect to create a self-perpetuating routine that requires zero maintenance once an initial schedule is established [cite: 2026-04-25]. To accommodate the ADHD brain's need for novelty and immediate dopamine, the app utilizes an "internal DOM" keyboard and a celebratory UI finale—triggering auditory and visual rewards like the "Matrix" or "Glitch" themes—to provide the high-energy feedback necessary for task completion [cite: 2026-04-25, 2026-04-27, 2026-04-29]. Furthermore, by shifting the recurring task logic from a reactive daily generator to a "look-ahead" completion system, the board ensures future visibility, allowing the user to anchor themselves in deep time while maintaining a fierce focus on the immediate present [cite: 2026-04-25].

## Implementation Strategy and Mechanics

The strategy outlined above is operationalized through the following architectural choices, functions, and methods in the codebase:

### 1. Externalisation & Time Blindness Mitigation
*   **Visual Deadline Conversion:** The system uses a visual progress bar system. Frontend templates (`index.html`) map the temporal distance to deadlines into width percentages.
*   **Kiosk Layout:** The interface is locked to a non-scrolling, high-contrast grid to ensure all critical data is immediately available without cognitive search costs.

### 2. Cognitive Load Management ("Top-Five")
*   **Method:** SQL queries in `app.py` enforce a strict `LIMIT 5` on active tasks, sorted by urgency (`ORDER BY deadline ASC`).
*   **Function:** `run_morning_briefing()` and the main dashboard route use this constraint to force prioritization and prevent choice paralysis.

### 3. Novelty & Dopamine Feedback
*   **Internal DOM Keyboard:** Custom JavaScript keyboards are injected directly into the DOM in `add.html` and `edit_task.html`. This prevents the OS keyboard from disrupting the layout and maintains the immersive kiosk feel.
*   **Celebratory Finale:** The `/complete/<int:task_id>` route handles the completion spike. It returns a randomized theme identifier (e.g., `matrix`, `glitch`) to trigger localized JS rendering effects.
*   **Auditory Reinforcement:** `trigger_voice_monkey()` fires API calls to Voice Monkey to deliver randomized praise or brutal nags. This leverages environmental audio to break hyperfocus or provide dopamine hits.

### 4. Self-Perpetuating Routine
*   **Look-Ahead System:** Handled by the `background_task_checker()` thread and the `recurring_templates` table. Instead of waiting for a user to trigger a new day, the system evaluates deadlines and generates the next iteration automatically upon completion or time trigger, ensuring the board is never blank.
