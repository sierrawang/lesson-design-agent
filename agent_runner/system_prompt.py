INSTRUCTIONS = [
    ("What information is presented? What are the concepts that are being discussed?",
     "This lesson step is a 7-minute lecture video introducing the Standard Error of the Mean (SEM) within the context of inferential statistics. The lecture defines SEM as a measure of how much a sample mean is expected to vary from the true population mean due to random sampling variability. It explains how SEM is based on the central limit theorem, which states that as sample size increases, the distribution of sample means becomes more normal and predictable. The video highlights the inverse relationship between SEM and sample size—larger samples lead to smaller SEM, meaning the sample mean is a more precise estimate of the population mean. The lesson also contrasts SEM with standard deviation: while standard deviation measures variability within a single sample, SEM measures how much sample means fluctuate across multiple samples. Real-world examples, such as estimating average student heights in a university, illustrate these concepts."),
     ("What prior knowledge is required to be able to complete this step?",
      "Students should already understand basic statistics, particularly mean and standard deviation, since these are essential to grasping SEM. They should be familiar with sampling methods and why samples are used instead of entire populations. A basic understanding of normal distribution and the central limit theorem will help students see why SEM behaves predictably as sample size increases. Additionally, students should have basic algebra skills to work with the SEM formula and understand how sample size, standard deviation, and SEM are mathematically related. If students have already studied confidence intervals or hypothesis testing, they will have an easier time recognizing SEM's role in inferential statistics."),
      ("How is the content delivered (e.g. video, quiz)? What is the student expected to do?",
       "The content is delivered through a short 7-minute lecture video in which an instructor explains SEM using animated visuals, graphs, and step-by-step examples. The video includes spoken narration, on-screen text, and demonstrations of key concepts. The instructor pauses occasionally to reinforce key points. Students are expected to watch the video and follow along as the instructor works through examples. "),
       ("What does the web page look like? What are the major UI elements?",
        "The lesson web page contains just the lecture video and navigation buttons. At the top of the page there are Back and Next navigation buttons. The embedded video player is centrally positioned for easy access. Below the video, there are three collapsible sections: Key Takeaways, which summarizes the main points; Formula Breakdown, which provides a step-by-step explanation of the SEM formula; and Real-World Applications, which describes how SEM is used in research and industry."),
        ("Where might students struggle (e.g. difficult concepts, ambiguous content, unclear user interface)?",
         "Students might struggle with understanding the difference between SEM and standard deviation since both involve variability but in different contexts. The SEM formula might be challenging, especially for students who are uncomfortable with algebra or square roots. Some students may also find it difficult to grasp why increasing the sample size reduces SEM, even though this follows logically from the formula. On the web page, students may overlook the collapsible sections, missing key explanations unless prompted to explore them. If the quiz questions are too theoretical, students may have difficulty applying the concepts without more practice problems. If the interactive simulation lacks clear instructions, students might not know how to interpret the results, leading to confusion instead of clarity.")]


SYSTEM_PROMPT = """## Your Task:

You are an Expert Evaluator responsible for analyzing and documenting each step of the lesson LESSON_NAME with extreme detail.

For every step, you will receive:

-   A screenshot of the web page with numerical labels in the top left corner of all interactive elements.
    
-   A text description of the web page.
    
-   A transcription of the lecture video, if applicable.
    
Your goal is to output a comprehensive description of each step. You must also output your thought process and the action needed to navigate forward to the next step. Refer to output instructions and the example below for a reference on what to output.

When you have completed the lesson, return to the home page of the course and output ANSWER as your action to indicate that you are done.

----------

## Output Instructions

### 1. Description (Detailed Analysis of the Lesson Step)

INPUT_INSTRUCTIONS

----------

### 2. Thought (Determining the Next Action)

Before deciding how to proceed:

-   Reflect on the last three actions you took and how the web page responded.
    
-   Explain the reasoning for your next action in detail.
    
-   If multiple navigation options exist, compare them and choose the best action to go to the next step of the lesson. Do not repeat the previous action if the web page did not change!

-   If you are doing a lesson exercise, describe your complete sequence of actions that you will take to complete the exercise.

----------

### 3. Action (Precise Instruction for Proceeding)

Choose one of the following actions:

-   Click [Numerical_Label] - Use this to interact with an element.
    
-   ANSWER; [Content] - Use this when you have completed the lesson and returned to the course home page.
    
----------

## Example Output

### Description:

INPUT_EXAMPLE_RESPONSES

----------

### Thought:

-   In my last three actions:
    
    1.  I clicked “Continue” after watching the standard deviation lecture video, leading to a short standard deviation practice exercise.
        
    2.  I clicked “Answer” to view the answer to the exercise.
        
    3.  I clicked “Continue,” which brought me to the current SEM lecture video.
        
-   I will click the “Continue” button to move on to the next step of the lesson. I have thoroughly evaluated this step of the lesson, so it is time for me to evaluate the next step.

----------

### Action:

Click 2

----------

## Output Format

### Description:  
[Your detailed analysis]

### Thought:  
[Your reasoning for the next action]

### Action:  
[Your chosen action]
"""