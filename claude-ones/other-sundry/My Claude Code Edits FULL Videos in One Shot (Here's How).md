# My Claude Code Edits FULL Videos in One Shot (Here's How)

[youtube.com](https://www.youtube.com/watch?v=mlhhZSHIS-w) · Brad | AI & Automation · 2026.08.06

> How can you make Claude edit videos autonomously in one shot? You must implement a **validation loop** using a "watch" skill, allowing the AI to see its own output and iteratively fix errors like a human editor.

- **Brad Bonanno** — Creator of the channel Brad | AI & Automation. · AI and workflow automation specialist teaching how to build autonomous AI systems.

> 💡 **Prerequisites**
>
> - [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) CLI / Desktop app.
> - [Whisper X](https://github.com/m-bain/whisperX) (for local transcription with word-level timestamps).
> - [FFmpeg](https://ffmpeg.org/) (for video and audio processing).
> - [Hyperframes](https://github.com/heygen-official/hyperframes) (open-source code-based graphics engine by HeyGen).
> - [Higgsfield MCP](https://higgsfield.ai/s/higgsfield-mcp-3-0-yt-bradbonanno-wmJubR) (for AI image and video B-roll generation).
> - Watch Skill & Editing Playbook (available via author's free playbook link).

![](https://resource.lilys.ai/images/genimg_096b4b5c8bd15575.png)

## 1. Overview of the AI Editing Pipeline

AI video editing breaks down human editing processes into discrete, automated stages that an agent can run . Because AI models like Claude Code cannot log directly into standard video software, the system relies on external CLI tools and APIs . The entire workflow runs on roughly five tools, most of which are completely free .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/0.jpg)

> 💡 **Core Goal of the Pipeline**
>
> To convert raw video footage into a fully edited final product—including cuts, AI B-roll, motion graphics, captions, and background music—in a single autonomous run .

### 1.1 The 5 Essential Pipeline Stages

1. **Transcription (Whisper X)** 
   - Converts raw footage into word-by-word text transcripts with subsecond timestamps .
   - Essential because Claude cannot listen to raw audio directly and needs exact timing to decide cut points .

2. **Rough Cut Trimming (FFmpeg)** 
   - Claude reads the timestamped transcript to identify bad takes, awkward silences, and filler words .
   - **FFmpeg** executes the physical trimming, joins trimmed clips back together, and cleans up the primary audio track .
   - Typically reduces 25 minutes of raw footage down to roughly 12 minutes of tight talking-head video .

3. **B-Roll Integration (Higgsfield MCP)** 
   - Claude checks screen recordings provided in project folders and merges them into relevant sections .
   - For script lines lacking user footage, Claude calls **Higgsfield** via its Model Context Protocol (MCP) to generate context-matched AI B-roll .

4. **Motion Graphics (Hyperframes)** 
   - Employs **Hyperframes**, a free, open-source graphics engine created by HeyGen .
   - Hyperframes builds graphics programmatically as HTML/code, eliminating design limits and allowing infinite visual creation .
   - Manages dynamic text, layout overlays, and visual scene transitions .

5. **Audio & Effects Layering (FFmpeg)** 
   - Layers background music tracks and sound effects over the trimmed video .
   - FFmpeg mixes multi-track audio to align perfectly with visual cues .

---

## 2. Cost and Efficiency Comparison

Running autonomous edits with AI significantly lowers overall production time and financial overhead compared to human editors.

> 💡 **Traditional Human Editor**
>
> - **Cost:** $150 to $3,000 per video .
> - **Turnaround Time:** Days to weeks .
> - **Feedback:** Manual back-and-forth communication required .
> 💡 **Claude Autonomous Pipeline**
>
> - **Cost:** ~$90 in API tokens (often covered under flat plans like Claude Code Max) + a few dollars per B-roll segment on Higgsfield .
> - **Turnaround Time:** ~3 hours complete edit .
> - **Feedback:** Self-correcting autonomous loop .

---

## 3. The Secret Weapon: The Watch Skill Agent Loop

Most standard AI video editing workflows fail because they generate a single output draft without reviewing it . Visual components often collide, captions cover faces, or graphics render off-center . Fixing these issues manually turns the creator into a "director for a blind editor," wasting hours .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/278.jpg)

### 3.1 Giving Claude Visual Sight

- Claude Code natively reads transcripts but cannot view visual frames .
- The custom **/watch skill** exports rendered video frames individually so Claude can visually evaluate screen elements .
- This unlocks a human-like editing process: making visual changes, watching the output, spotting errors, and refining the layout .

### 3.2 The Agentic Validation Loop

![](https://resource.lilys.ai/images/genimg_27e802f3c1bdf3aa.png)

1. **Initial Rendering:** The pipeline compiles a draft video using FFmpeg and Hyperframes .
2. **Sub-Agent Review:** Autonomous sub-agents execute the **/watch skill** frame-by-frame .
   - Sub-agents look for visual glitches, overlapping text, spacing errors, and poor alignment .
3. **Fix List Generation:** Sub-agents aggregate issues into a clear bug list sent directly to Claude .
4. **Autonomous Re-rendering:** Claude updates the graphic code, re-renders the video, and re-triggers validation .
5. **Final Approval:** The loop repeats autonomously until the edit passes quality thresholds .

---

## 4. Step-by-Step System Setup

Setting up the editing workspace requires creating a dedicated project directory and installing key developer packages inside Claude Code .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/403.jpg)

### 4.1 Folder and MCP Configuration Steps

1. **Create Project Folder:** Create a folder named `video_editor` on your computer and open it within Claude Code .
2. **Install Watch Skill & Hyperframes:** Download the watch skill scripts and point Claude Code to the Hyperframes GitHub repository to install dependencies .
3. **Connect Higgsfield MCP:**
   - Navigate to `higgsfield.ai/mcp` and copy the endpoint URL .
   - Tell Claude to add the MCP link to your active workspace or Claude Chat connectors .
4. **Install FFmpeg & Whisper X:** Provide the respective GitHub/download links to Claude to install both local processing tools .

---

## 5. Live Demonstration: One-Shot Intro Edit

To test the fully configured pipeline, Brad edits a video intro completely autonomously from raw files .

### 5.1 Preparing Pre-Work Assets

- Gather raw camera clips and script documents into a single source folder .
- Add comments directly within the document (e.g., Google Doc or Word) specifying:
  - Background music tracks to use .
  - Camera zoom instructions (e.g., start zoomed in, rapidly zoom out) .
  - Graphic style requests and links to reference images .

> 💡 **Critical Pre-Work Principle**
>
> Without explicit instructions and script comments, AI editors generate generic "AI slop." Spending 10 minutes annotating the script saves hours of revision time .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/561.jpg)

### 5.2 Execution Phase

1. **Initiate Command:** Provide Claude with the source file directory address and instruct it to read the document comments and run the **/watch skill** loop .
2. **Directory Scaffolding & Asset Gathering:** Claude creates a project structure (`assets/`, `renders/`) and downloads external links or audio files .
3. **Whisper X Transcription:** Whisper X produces exact word-level timecodes .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/617.jpg)

4. **Rough Cut Generation:** FFmpeg cuts raw footage (1 min 30 sec) down to 39 seconds of clean dialogue .
5. **AI B-Roll & Graphics Generation:**
   - Higgsfield renders requested 1080p B-roll scenes .
   - Hyperframes generates code-based graphic overlays matching script context .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/737.jpg)

6. **Self-Improvement Loop:** Claude inspects draft renders frame-by-frame, corrects graphic placements, and performs technical Q&A passes autonomously .

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/mlhhZSHIS-w/827.jpg)

---

## 6. Four Secrets for True One-Shot AI Edits

Beyond core tools, four specific strategies elevate AI edits to high quality on the first try .

```
[Taste Skill] --------> Enhances Front-End HTML Design
[Mid-Edit Assets] ----> Blends Higgsfield Visuals into Hyperframes
[Style File Memory] --> Retains Corrections for Future Edits
[Script Pre-Work] ----> Eliminates Guesswork via Direct Notes
```

1. **The Taste Skill** 
   - Since Hyperframes renders graphics using HTML/CSS, front-end design principles directly govern quality .
   - The taste skill gives Claude strict visual rules (spacing, typography, alignment) to prevent default "AI slop" visuals .

2. **Mid-Edit Asset Generation** 
   - Claude uses Higgsfield mid-edit to generate unique icons, images, or motion elements .
   - Hyperframes embeds these generated media elements directly inside dynamic HTML graphics .

3. **Self-Updating Style File** 
   - Whenever you provide manual review notes, save those corrections permanently into a project `style.md` file .
   - Claude consults this style file on every subsequent video, preventing repeated errors over time .

4. **Detailed Pre-Work & Script Annotations** 
   - Annotating script documents with specific asset requirements is the single most important factor for success .
   - Clear script comments completely remove agent guesswork, ensuring accurate edits in one shot .
