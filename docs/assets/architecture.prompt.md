# Architecture image generation

Generated with the built-in image generation tool.

## Initial prompt

Create a razor-sharp high-resolution flat architecture infographic for a GitHub documentation page, Claramap Builder. Landscape 3:2 canvas approximately 2400x1600, white background, clean modern sans-serif type, generous whitespace, deep forest green headings, warm orange iteration arrow, restrained pale green and light gray cards. This is a technical explanatory diagram, NOT a decorative 3D illustration. All labels must be large readable and typeset perfectly. No textures, no shadows, no gradients, no tiny text, no logos.
Title top left exactly "Claramap Builder". Subtitle exactly "Architecture".
Layout: At top a wide pale green banner reads "AgentSkill" with subtitle "Instructions · Templates · Helpers". A smaller card attached to its right reads "SpecFlow" with subtitle "Planning method". One arrow from SpecFlow INTO AgentSkill labeled "Structures the plan". A short arrow from AgentSkill down to the coordinator shows it instructs coordinator.
The dominant middle row is a simple left-to-right pipeline with four equal generous cards, each with a number:
"1  Claude Code" / "Coordinate & delegate"
"2  Codex workers" / "Scoped tasks & context"
"3  Claude Code" / "Validate & integrate"
"4  Claude reviewer" / "Independent review"
Connect exactly in sequence with clean thick arrows. Above first card a small label "Your goal" points down into first card. Beneath the middle row a clearly separated orange feedback arrow runs leftward from cards 3 and 4 back to card 1, labeled "Failed checks or findings → repair". Beneath card 4 a short green arrow points to green outlined pill "Built & checked code". Keep this output separate from the orange loop.
Bottom is an evidence band: two cards "SpecStory" / "Conversation capture" and "Run records" / "Attempts · Checks · Reviews". Dotted vertical connections from build pipeline to these cards show evidence capture, with NO crossing of words. These two evidence cards connect to a third card "/improve-workflow" / "Analyze runs when requested". Beside this bottom row or below it a brief note exactly "Improvements applied only when requested".
Keep every edge unambiguous, avoid tangled connections, prioritise hierarchy and readability at 900px display width. No extra text. All elements fully inside comfortable margins.

## Correction prompt

Edit this architecture diagram, preserving all typography, cards, colors, text and overall layout. Correct ONLY three sets of connections: (1) The arrow from the AgentSkill banner currently incorrectly points into Codex workers. Route it with a right-angle elbow through the clear whitespace above the build row and point it down into the top of card 1 Claude Code. Keep 'Instructs coordinator' beside this routed arrow without colliding with other text. No arrow from AgentSkill into Codex. (2) The orange repair loop has an upward arrow into card 3. Reverse that short segment so it flows DOWN out of card 3 into the orange return line. The loop flows from card 3 and card 4 LEFT back into card 1 only. (3) Remove the horizontal arrow from SpecStory into Run records. These are independent evidence sources. Keep Run records pointing right into /improve-workflow, and draw a separate elbow connection from the bottom of SpecStory, along a clear bottom margin, then into the bottom of /improve-workflow. Move the small 'Improvements applied only when requested' note down if necessary, ensuring no overlap. No other changes. Crisp clean arrowheads and ample whitespace.

