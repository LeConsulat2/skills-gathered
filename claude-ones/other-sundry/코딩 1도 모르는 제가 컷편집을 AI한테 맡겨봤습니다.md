# 코딩 1도 모르는 제가 컷편집을 AI한테 맡겨봤습니다

[youtube.com](https://www.youtube.com/watch?v=UNH8qfgVzaw) · 동테크 · 2026.08.07

> Can you automate video editing without knowing how to code? By using **AI-driven research and iterative feedback**, you can build custom automation tools that shift your focus from manual labor to high-value creative strategy.

- **DongTech (동테크)** — AI content creator and YouTuber focusing on practical AI workflows. · Demonstrates no-code/vibe coding techniques using LLM tools like OpenAI Codex.

> 💡 **Prerequisites**
>
> - **GPT App / Codex**: Desktop AI agent interface (Windows/macOS) 
> - **CapCut Desktop**: Video editing software 
> - **Microphone**: Desktop or earphone microphone for quick voice input

![](https://resource.lilys.ai/images/genimg_97608fe054d4b68b.png)

## 1. Setting Up Codex for Automated Video Editing 

### 1.1 Goal and Setup Environment 

The creator attempts to build an automated video cut-editing system inside **CapCut** using **Codex** within a tight 1-hour time limit. 

- The test clip is a 1-minute video containing recording mistakes, verbal slips, and repeated takes. 
- The objective is to evaluate whether **Codex** can automatically edit out mistakes without manual coding knowledge. 

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/UNH8qfgVzaw/18.jpg)

### 1.2 Installing and Configuring Codex 

1. **Installation**: Search for the GPT app or Codex download page and install the client suited to your OS (macOS or Windows). 
2. **Selecting the Tool**: Open the app and choose **Codex** from the top-left menu to enable voice-driven vibe coding. 
3. **Project Creation**: Click "New Project" and specify a local directory folder (e.g., `codex_video_cut`) for the AI to work in. 
4. **Model Settings**:
   - **Model**: Select `5.6-sol` or a similar recommended baseline model. 
   - **Reasoning Effort**: Set to `High` or `Very High` (use `Ultra` only for extremely difficult engineering problems). 
   - **Speed**: Set to `Fast` if tokens permit, or `Standard` for cost savings or complex tasks. 

---

## 2. Deep Research Strategy for Vibe Coding 

### 2.1 Using Voice Prompts 

Using voice dictation prevents creative ideas from disappearing while typing. 

- On Windows, press `Win + H` to activate voice recording. 
- On macOS, press `Command` twice to start voice input. 

### 2.2 Directing AI to Research Solutions 

Instead of manually reading documentation, instruct Codex to perform a deep research search across online video platforms and blogs. 

> 💡 **Effective Deep Research Prompting**
>
> - Ask the AI to target high-performing global content (e.g., search videos with over 50,000 views). 
> - High view counts signal proven, reliable scripts or workflows. 
> - Use the **Adjust Current Task** feature to override existing actions and force immediate deep research on new criteria.

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/UNH8qfgVzaw/208.jpg)

### 2.3 Utilizing Existing Developer Skills (GitHub Repositories) 

Codex discovers open-source tools such as `pycapcut` on GitHub during its research. 

- Developers frequently share pre-built solutions for common automation problems on **GitHub**. 
- Vibe coding allows users to plug in these pre-built community scripts rather than building system pipelines from scratch. 

---

## 3. System Implementation and Control Permission Setup 

### 3.1 Providing Editing Context to the AI 

Provide detailed context about your specific recording style so the AI can build a tailored pipeline: 

- State the niche (e.g., AI/tech informational content). 
- Explain the flaw (e.g., frequent verbal slips causing redundant duplicate segments). 
- Define the target task (e.g., trim bad takes, remove unnecessary silences, retain optimal phrasing). 

### 3.2 Desktop Control Permissions and Safety Considerations 

Codex uses computer vision and automated mouse/keyboard controls (`computer_use`) to directly operate software applications. 

> 💡 **Request Approval Mode**
>
> - Prompts the user before executing every single action. 
> - **Pros**: Prevents unintended operations or accidental data loss. 
> - **Cons**: Requires continuous manual clicking, slowing down automation.
> 💡 **Full Permission Mode**
>
> - Grants the AI unrestricted control over mouse and filesystem actions. 
> - **Pros**: Fully autonomous hands-free execution. 
> - **Cons**: Poses risks of accidental deletion of local files or existing projects.

### 3.3 Course-Correcting Efficient Workflows 

When Codex incorrectly attempts to transcribe a full 65-minute raw file instead of editing the target clip inside CapCut, halt the execution immediately. 

- Stop wasteful long-running background tasks to save time and API quota. 
- Redirect the prompt toward using localized native CapCut features or API scripts. 

---

## 4. Execution, Feedback Loops, and Refinement 

### 4.1 Running the Generated Cut-Editor 

Codex generates a localized Python tool and interface within 15 minutes. 

1. Open the project output folder via File Explorer. 
2. Launch the generated script file (e.g., `Cut Editor Execution`). 
3. Select the active CapCut track and click **Execute Cut Edit**. 

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/UNH8qfgVzaw/746.jpg)

### 4.2 Iterative Quality Control and Error Correction 

Initial AI automation outputs often contain minor flaws that require iterative user feedback. 

```
[ Feedback Loop ]
Observe Output Video ──> Identify Errors (Silences / Choppy Trims) ──> Provide Specific Timestamps ──> AI Refines Rules
```

1. **Issue Identification**: The first pass cut-edited clip retained empty spaces and left unedited duplicate sentences. 
2. **Diagnosing Root Cause**: The AI explained that subtle camera movements led it to falsely identify static pauses as active visual content. 
3. **Specific Directives**:
   - Explicitly define strict silence removal rules to maximize information density. 
   - Provide exact timestamps (e.g., "10s–12s contains duplicate phrasing") to help the model fix its sentence boundary algorithms. 

---

## 5. Practical Vibe Coding Application Case: AI Landing Page 

### 5.1 Case Study: Non-Designer Creating a Sales Page 

Vibe coding applies to graphic design and landing page creation without design software skills. 

- The author used Codex to analyze landing page structures from leading platforms like FastCampus and Coloso. 
- **Codex Automated Tasks**:
  - Researched persuasive copywriting frameworks. 
  - Fetched market price statistics and captured comparative screenshots. 
  - Generated visual layout assets, motion GIFs, and targeted blur effects. 

![](https://resource-release.s3.ap-northeast-2.amazonaws.com/thumbnails/UNH8qfgVzaw/1024.jpg)

### 5.2 The Core Value of Automation 

> "By reducing manual editing resource overhead, creators can allocate up to 80% of their effort toward high-value content planning and scripting." 

- Vibe coding relies on persistence and clear problem definition rather than manual software execution. 
- Mastering AI research loops enables non-developers to build automated systems for specialized personal and commercial tasks.
