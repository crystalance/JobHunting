# Amazon VO Preparation

> Section: **Interview** — extracted from leetcode_solution.md (lines 4191-4605)

## Amazon VO preparation (let's f**king get it!)



### lru

```java
class LRU{
  class Node{
    int key;
    int val;
    Node prev;
    Node next;
    public Node(int key, int val){
      this.key 
      this.val = val;
    }
  }
  int capacity;
  Node head;
  Node tail;
  Map<Integer, Node> map;
  
  public LRU(int capacity){
    this.capacity=capacity;
    head=new Node(-1,-1);
    tail = new Node(-1,-1);
    map = new HashMap<>();
    
    head.next = tail;
    tail.prev = head;
  }
  
  
  
  
  //helper
  
  public void put(){
    //if already contains, remove old one
    if()
      
      // new a Node, 
      // update map
      // update linkedlist
      
      
      // if size > capacity
      // remove end 
    
  }
  
  
  
  
  
  
  
  
  
}
```



### OOD

1. 









### 0. Self-introduction

1. Hello, my name is Weikai Liao, and I'm currently a Master student studying software engineering at Duke University. I have a strong passion for software development and have gained practical experience through projects and internships.
2. During my internship at BoulderAI Technologies from April to June 2024, I engineered a Large Language Model bot using FastGPT to transform natural language into BPMN diagrams, developed automation tools for data management, and implemented workflows using a low-code platform. These projects enhanced efficiency and automation, reducing manual effort. 
3. During my internship, I focused on collaboration and quickly integrating into a complex system. I utilized GitLab for multi-version control and configured projects using Nacos. I developed APIs within a microservices architecture and learned to test them locally using a shared development environment. I also learned the importance of quickly integrating into an existing, complex system and efficiently reading and understanding others' code. Working closely with my mentor and team leader, I effectively navigated challenges and contributed to successful project outcomes
4. Thank you for considering my application.I'm excited about the opportunity at Amazon

### 1. BQ questions 

1. method

   1. TASK
   2. https://docs.google.com/document/d/112HBiMNvu6TYbDUOfVRe_MS4A-fKaWYrpMlmnsiMNiA/edit?tab=t.0
   3. 

2. questions

   1. most impactful project

3. Leadership principles 

   1. Bias for action

      1. key words: speed, **calculated risk** 
      2. 
      3. **tight deadline** (Bias for action)(customer obsession)

         1. first edition 

            1. During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify workflow creation, enabling project managers to effectively design workflows.

               Facing a tight deadline, I had to choose between two LLM models: one was faster and cheaper but less accurate, while the other was more accurate but slower and costlier. Given our objective to empower project managers with a user-friendly tool, I prioritized accuracy to ensure reliable workflows.

               Before making a decision, I took action to collect essential data. I gathered insights from our development team and analyzed feedback from previous projects highlighting the importance of accuracy. I discovered that high-quality outputs significantly reduced user frustration and errors in workflow creation.

               After deciding on the more accurate model, I quickly iterated several versions to optimize performance despite the slower processing time. This resulted in a 30% decrease in user revisions and increased confidence in constructing accurate workflows independently.

               By prioritizing data-driven decisions and fast iterations, we enhanced the user experience, aligning with our mission to simplify workflow creation. This taught me the importance of balancing immediate challenges with long-term benefits, ultimately leading to greater efficiency and user satisfaction.
         
         2. Second edition
         
            1. **Tight Deadline Story (Bias for Action, Customer Obsession)**
         
               During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify workflow creation, enabling project managers to effectively design workflows.
         
               **Facing a tight deadline**, I had to quickly choose between two LLM models: one was faster and cheaper but less accurate, while the other was more accurate but slower and costlier. Given our objective to empower project managers with a user-friendly tool, I prioritized accuracy to ensure reliable workflows.
         
               To make an informed decision swiftly, I coordinated closely with cross-functional teams. I organized rapid feedback sessions with the development team and engaged in quick discussions with customer support to gather insights from previous projects. This highlighted the critical importance of accuracy in reducing user frustration and errors.
         
               After selecting the more accurate model, I communicated regularly with the team to iterate several versions rapidly, optimizing performance despite the slower processing time. We held daily stand-ups to keep everyone aligned and used collaborative tools to track progress and share updates in real-time.
         
               This approach resulted in a 30% decrease in user revisions and increased confidence in constructing accurate workflows independently. By prioritizing data-driven decisions and fast iterations, we enhanced the user experience, aligning with our mission to simplify workflow creation. This experience taught me the value of effective communication and collaboration under pressure, balancing immediate challenges with long-term benefits to achieve greater efficiency and user satisfaction.
         
      4. Limited info

         1. During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify the workflow creation process, enabling project managers—rather than just professional programmers—to effectively design workflows.

            While engineering the bot, I faced a critical decision between two LLM models. One model was faster and less expensive but sometimes produced less accurate results. The other model was more accurate but slower and costlier to implement. Given our objective to empower project managers with a user-friendly tool, I recognized that accuracy was paramount to ensure that the generated workflows were reliable and effective.

            To make an informed decision, I gathered insights from our development team and analyzed feedback from previous projects that emphasized the importance of content accuracy for end users. Although I had limited information on how the slower processing times might impact user experience, I discovered that high-quality outputs significantly reduced user frustration and errors in workflow creation.

            Ultimately, I chose the more accurate model, despite its higher cost. This decision resulted in a 30% decrease in the number of revisions required by users when creating workflows. Users reported increased confidence in their ability to construct accurate workflows independently, significantly enhancing their overall experience with the tool.

            By prioritizing accuracy over speed and cost, we not only aligned with our mission to simplify workflow creation for project managers but also demonstrated a commitment to **Customer Obsession**. This experience taught me the importance of making data-driven decisions, especially when aiming to empower users with innovative solutions, even if it meant investing more upfront. Ultimately, the long-term benefits of accuracy outweighed the initial costs, leading to greater efficiency and satisfaction among our users.

   2. Ownership

      1. above and beyond （**Outside responsibility**）

         1. 初始版本：下面是我这个故事的细节（要求用star原则）：老板要求我们team为公司的平台开发一个new feature的原型：开发一个利用ai自动生成的工作流程图的功能，我的职责是写prompt开发那个ai bot，它可以将自然语言转化为json格式的流程图数据。然后开发完成后和mentor对接，也成功将api对接进了系统，并能在前端成功显示流程图，但我是一个喜欢从客户角度出发测试产品品质的人， 我详细测试了产品，发现每当我提出很详细的要求时，前端无法正常显示流程图，但是我查看ai bot的日志时他是能正常生成数据的。然后我又经过细致的排查，利用浏览器f12发现是后端api超时了，超过2分钟的全都超时，我没有权限改这个config,然后就找我mentor一起修改，问题最终解决，大大提高了这个功能按要求生成复杂流程图的能力。

         2. Version1:
            1. **Situation:** Our team was tasked with developing a new feature for our company's platform: an AI-driven workflow diagram generator. My role was to create prompts for the AI bot to convert natural language into JSON format for the diagrams.
            2. **Task:** After successfully integrating the API and displaying the diagrams on the front end, I decided to test the product further from a customer perspective. I noticed that when I input detailed requests,  the diagrams failed to display properly, though the AI bot's logs showed correct data generation.
            3. **Action:** I conducted a thorough analysis and discovered, using the browser's developer tools, that the backend API was timing out after two minutes, causing the display issue. The configuration to change this was beyond my permissions. With the owner on vacation, I took the initiative to address this issue immediately, considering the potential negative impact on our users.\
            4. I collaborated with my mentor to adjust the API timeout settings, ensuring the feature could handle complex requests. I also documented the problem and solution, then emailed the owner upon their return, suggesting further improvements.
            5. **Result:** This proactive approach significantly enhanced the feature's capability to generate complex workflow diagrams, improving user satisfaction and retention. By stepping outside my assigned role, I ensured a seamless user experience and demonstrated long-term thinking and ownership.

      2. Pushback & conflicting

         1. sacrifice short term gains for long term goals

            1. main point:

               1.  Short-term vs long term 

               2. During my internship at BoulderAI Technologies, I was tasked with enhancing BPMN diagrams by linking them to existing workflows. I faced a decision between a short-term solution of manually linking processes to meet an upcoming deadline and a long-term solution using RAG technology to automate integration with our knowledge base.

                  I discussed both options with my supervisor, advocating for the long-term approach. I explained how RAG technology would provide sustainable benefits and reduce future workload. To mitigate the risk of missing the deadline, I broke down tasks and identified reusable components from our systems that could return task template names and IDs. I imported this data into the LLM’s knowledge base, allowing the system to automatically generate accurate and integrated workflows.

                  By optimizing the development process and re-prioritizing tasks, we implemented the RAG-based solution before the deadline. This not only improved functionality and reliability but also enhanced user satisfaction by streamlining operations and aligning with our long-term goals.

   3. are right, a lot 

      1. Mistake/failure 类问题

         1. Miss ddl. one time you failed/biggest mistake

            1. project in undergraduates

               1. idea

                  1. 
                  2. underestimate & (**most important: **)
                     1. 可以错的点：
                        1. Misjudged the 
                        2. focus on too much on detail
                        3. (写自己的错)
                  
                  3. teachers's requriement is vague, just let us use a java framework called spring and other frontend language  to create a full-stack web application making a . As a team leader of my team i was responsible for backend development and let my teammates to learn frontend. as we are both new to the web development at that time, we knows little about how to coordinate frontend and backend. and unfortunately my teammates was not positive and responsive. when i ask him about progress, he always says there's some bug and his working on it. But he was my friend and I'm not pushing him for the sake of friendship. at last i he didn't make his part and i have to help him to do it. eventually we missed ddl and asked extension from professor for one week to re implement frontend and coordinate with ,backend  worked as hard i as can and finally make up.  
                  
                  This experience **taught me the importance of ensuring clear and continuous communication between teams**. I learned to establish more thorough documentation and regular synchronization meetings to verify that all teams are aligned on technical specifications.
   
         2. interpersonal conflict 类问题
   
            1. How you resolve conflict with your teammates
   
            2. Whether or not to implement  segmented file upload feature under limited time
   
               1. **Situation:** In our undergraduate project team, we were tasked with enhancing a centralized family file management solution for our classmates and professor. One proposal was to implement a segmented file upload feature to increase transfer speed and allow resumption of interrupted uploads.
   
                  **Task:** Our team was divided. I supported the feature, believing it would enhance user experience for students and faculty. However, a teammate was worried about the complexity it would add, given our limited timeline.
   
                  **Action:** I communicated my perspective, highlighting the long-term benefits and improved user satisfaction from faster uploads and reliable resumption. I acknowledged my teammate's concerns about time constraints and proposed a small-scale proof of concept to assess feasibility within our deadline.
   
                  While breaking down the project into smaller tasks, I discovered an API we could reuse, significantly reducing development time since we didn't have to build it from scratch. To mitigate risks, we agreed on a plan to allocate resources efficiently and set clear milestones for progress evaluation.
   
                  **Result:** The proof of concept showed significant improvements in upload speed, and feedback from our classmates and professor was overwhelmingly positive. We successfully implemented the feature, resulting in a 30% increase in user engagement. My teammate later appreciated the collaborative approach and recognized the positive impact on our project.
   
      2. Customer obsession
   
      3. Think Big
   
         1. Most challenge in previous job?
   
         2. 
   
      4. Invent & Simplify
   
      5. Learn, and Be Curious
   
      6. Dive Deep
   
      7. Insist On The Highest Standards
   
      8. Earn Trust
   
      9. Deliver Results
   
   4. 

### 2. potential coding problems

1. Leetcode 545 

2. Leetcode 45

   1. While(boundary){

      1. While(){}

      }


3. lc 200

### 3. 面筋

1. VO：20分钟bq，问了out of duty和w/o enough info to make decision，每个故事会问两个follow up问题。20分钟算法题考了用最小堆解决问题，问了优化follow up。
2. VO的前20-30分钟bq 只问了一个out of responsibility 的问题，其余时间都是技术问题细节，eg. design patterns，API design，scalability etc.
   1. （个人猜测可能是挂在这里了，他问的好多tech细节内容都忘记了， 瞎回答的，design pattern这块是真的不知道）coding 参考LC 溜耳伊。 
   2. （coding应该没问题，给面试官讲完思路后他赞同然后开始写，vo 结束后自己又跑了一遍）
   3. 经验总结： 还是要对自己做过的project非常熟悉。之前花太多精力在coding上面了，忽略了八股这方面。
   4. 

### 4. Good problem worth reviewing

1. leetcode 2055

   1. sometimes we can reach o(n) time complexity by recording addtional information using additional array or sth
   2. more examples 
      1. leetcode 155
         1. use a hashmap to recorde the minimum value of each state;

2. backtrack

   1. when remove, make sure you remove the right element, it should be the last element you added into data structure 
   2. ![Screenshot 2025-01-26 at 23.51.09](/Users/lanceliao/Desktop/Screenshot 2025-01-26 at 23.51.09.png)

3. leetcode 138

4. 1642

   1. Greedy 
      1. 用无穷长的ladder 替换bricks


### 5. what should i do at the coding part?

1. asking clarification  question
   1. about input data
   2. Write a solution at first and optimized it later
   3. take some time write a case that's not a happy case to test your code
   4. Don't forget to include time complexity
   5. time your self taking those exercises
2. 

### 6.  finnal bq answer



#### 1. Tight ddl

-------

During my internship at BoulderAI Technologies, I was tasked with developing an AI assistant to convert natural language into business process workflows. Initially, we had a month to create a prototype for a customer demonstration. However, my manager unexpectedly cut the deadline to two weeks to align with an important client meeting.

Faced with this tight deadline, I realized I couldn't include all the features we initially discussed. After consulting with my manager, we agreed to focus on delivering a functional prototype by cutting non-essential features and optimizing critical performance aspects. For example, I initially planned to connect the database to the AI knowledge platform for automatic data retrieval using RAG technology to enhance performance. But I had no time for that. Instead, I manually imported data to ensure the demonstration's effectiveness.

I sought assistance from my mentor, who quickly helped me familiarize myself with the AI platform to avoid process delays due to potential bugs.

By collaborating closely with cross-functional teams from both the backend and frontend, we successfully launched the product feature on schedule, surpassing user adoption targets. Feedback from my supervisors highlighted the effectiveness of my approach, and I learned the importance of strategic prioritization and teamwork in meeting tight deadlines.

#### 2. out of responsibility

------

1. **Situation:** Our team was tasked with developing a new feature for the company's platform: an AI-driven workflow diagram generator. My responsibility was to develop the AI application using the AI knowledge platform called FastGPT, ensuring it correctly returned desired results from prompts.
2. **Task:** After developing the AI application and testing the generated data,  my part is over. but I wanted to test the feature from a user perspective to see if it works. I found that simple requests worked well, but complex requests failed to display correctly on the front end. The AI logs showed correct data generation, which means my part is fine, indicating an issue elsewhere.
3. **Action:** Facing this problem, I felt an urge to solve it or at least report the problem to ensure a seamless experience for customers.  I conducted a thorough analysis and discovered that the backend API was timing out after two minutes, which caused the display issue. Since I was responsible only for developing the AI application and not integrating the API with the backend, I didn't have the authority to change the timeout settings. Recognizing the importance of resolving this, I scheduled a brief meeting with my supervisor, presenting the data and clearly explaining the timeout problem and its impact on user experience. explaining that while the AI application worked locally, it faced integration issues. He helped me to find who's reponsible for this. And I then coordinated with the responsible colleague to adjust the timeout settings.
4. **Result:** This proactive approach improved the feature's ability to handle complex requests, significantly enhancing user satisfaction.

##### 2.1 possible follow ups

1. Certainly!

   1. **Communication:** How did you approach your supervisor and colleague to discuss the timeout issue?
      - I scheduled a brief meeting with my supervisor, presenting the data and clearly explaining the timeout problem and its impact on user experience. I focused on collaboration to find a solution.

   2. **Collaboration:** How did you coordinate with the colleague responsible for the backend to implement the necessary changes?
      - I reached out to the colleague via a quick chat, shared my findings, and we reviewed the API settings together. We then worked as a team to adjust the timeout settings and ensured thorough testing.

   3. **Initiative:** What motivated you to go beyond your initial responsibilities and test the feature from a user perspective?
      - I wanted to ensure a seamless user experience and believe that understanding the end-user perspective is crucial for delivering high-quality products.

   4. **Challenge Handling:** Did you face any resistance or challenges when proposing the changes to the backend settings?
      - Initially, there was some hesitation about changing the timeout settings. I addressed this by presenting evidence of the issue and demonstrating the benefits for the project’s goals, gaining support through data and user impact.

   5. **Outcome Measurement:** How did you measure the improvement in user satisfaction and retention after resolving the issue?
      - We analyzed user feedback and tracked metrics such as request completion rates and user engagement before and after the change. Positive feedback and increased retention rates confirmed our solution's success.

   6. **Learning:** What key lessons did you take away from this experience, and how have they influenced your approach to subsequent projects?
      - I learned the importance of looking beyond immediate responsibilities for project success and the value of effective communication and collaboration. These lessons have made me more proactive and solution-oriented in future projects.

#### 3.  help peers, 

-------------------

During a university project, we were tasked with creating a full-stack web application to implement a mini Uber using Django  for the backend and React for the frontend. As the team leader, I was responsible for the backend, while a teammate handled the frontend. However, my teammate was new to web development and unsure about effectively coordinating the two aspects. 

The project's success relied on seamless integration between the frontend and backend, and his struggle with the frontend was critical to our completion. 

Recognizing the issue, I stepped in to assist. I showcased a demo featuring user registration and login to help him understand RESTful APIs, wrote a clear API document detailing the expected data, and explained it to him. Once he grasped the overall framework, he began to learn quickly and took charge of the frontend development. I also initiated regular check-ins to ensure he wasn't blocked for long periods. 

As a result, our project was completed on time and received high marks for its functionality and integration. This experience not only boosted my teammate's confidence but also strengthened our collaborative skills.



#### most challenging project, 

--------------------------------

1. One of my most challenging projects was developing a family-oriented cloud storage system during my undergraduate studies.
2. The challenge stemmed from high demanding performance requirements from my instructors, he wish us to lower the reponding time below 300 ms for file searching feature
3. Initially, we planned to use MySQL's `LIKE` statement for implementing the fuzzy search for the file search feature. However, testing revealed that as the number of stored files increased to over 50,000, response times slowed significantly, from an average of 600ms to over 2 seconds, degrading user experience. 
4. To address this, I leveraged online resources, including technical articles and forums, to understand the limitations of using MySQL for searching, which results in a time complexity of O(n). I learned about inverted index technology, which can achieve O(log(n)) search time, and discovered that Elasticsearch, a non-relational database, utilizes this technique.
5. I quickly learned how to implement Elasticsearch for fuzzy searching by studying documentation and tutorials. This reduced the average response time to under 100ms, significantly enhancing the application's performance. This experience required prioritizing tasks, breaking them into manageable parts, and rapidly acquiring new skills through self-directed learning.
6. Despite the complexity, we successfully delivered a robust application on schedule, enhancing user satisfaction and productivity.

#### calculated risk | limited info

-----------------------------------------------------

During my internship at BoulderAI Technologies from April to June 2024, I worked on developing an LLM bot using FastGPT to convert natural language into BPMN diagrams. The goal was to simplify the workflow creation process, enabling project managers—rather than just professional programmers—to effectively design workflows.

While engineering the bot, I faced a critical decision between two LLM models. We tested both models using 100 test cases to evaluate the accuracy of their results with the same input and output. We found that Model A had a 20% higher cost and a 25% longer response time, but it delivered results that were 15% more accurate than Model B. Given the time and resource limitations of only having 100 test cases, I questioned whether this sample was representative enough to draw definitive conclusions about overall performance.

At that moment, I recognized the need for a trade-off. Our product was designed for project managers, who would find it challenging to modify the generated process diagrams. Therefore, ensuring successful generation on the first attempt was crucial, even if it meant sacrificing some speed and cost for that additional 15% accuracy.

With this analysis, I presented my findings to my manager, who agreed with my perspective. Ultimately, we opted to use the more accurate model, which improved the precision and effectiveness of the generated results. Enventually the user expressed high satisfaction and indicated they were willing to accept a modest increase in cost and response time, as they valued the enhanced accuracy and reliability of the tool.

This experience taught me the importance of making data-driven decisions, especially when aiming to empower users with innovative solutions, even if it meant investing more upfront. Ultimately, the long-term benefits of accuracy outweighed the initial costs, leading to greater efficiency and satisfaction among our users.

#### biggest mistake ｜ miss ddl

-----------------

Mistake? Waste too much time on choosing things? 

1. 没有做好priority, 在一个不太重要的地方被block住了很长时间（分清主次）
2. （never underestimate task） 如果要重来一遍的话 要把任务划分成几个点，把具体的任务细节化，然后给每个任务进行评估
3. 事情不对劲，应该提早地transparent到上级（team），不应该在最后一刻才告知.

----

**Situation:**Smart Home system While working on the user management system and designing a WebSocket communication protocol, I faced challenges that ultimately led to missing the project deadline.

**Task:** My responsibilities included developing user management features and establishing a robust WebSocket protocol. However, I became overly focused on optimizing performance with Redis caching, which took up a significant amount of my time.

**Action:** By dedicating too much effort to the caching implementation, I neglected the design of the WebSocket protocol, leaving insufficient time to create a solid and effective solution. Additionally, I did not communicate my challenges to the team early enough, which hindered our collective progress.

**Result:** As a result, I missed the deadline, causing delays not only in my work but also for the entire team, as the WebSocket protocol was essential for real-time communication.

**Learning:** This experience taught me the importance of prioritization, effective task management, and open communication. I learned to balance performance optimizations with foundational tasks, ensuring that I allocate time appropriately. I also recognized the need to be transparent with my team about challenges, allowing for collaborative problem-solving. Moving forward, I actively applied these lessons to improve project outcomes and foster a supportive team environment. The miss ddl situation never happened again 

As an engineer, facing choices is constant. It's often hard to determine the right path, but it's crucial to keep moving forward and make incremental progress. Even if some attempts fail, they help rule out possibilities, contributing to overall progress.

#### conflict with others

------

**Situation:** In our undergraduate project team, we were tasked with developing a centralized family file management solution. Our team was divided about whether or not we should implement a segmented file upload feature to increase transfer speed and allow resumption of interrupted uploads.

**Task:** . I supported the feature, believing it would enhance user experience for students and faculty. However, a teammate was worried about the complexity it would add, given our limited timeline.

**Action:** I communicated my perspective, highlighting the long-term benefits and improved user satisfaction from faster uploads and reliable resumption. I acknowledged my teammate's concerns about time constraints and proposed a small-scale proof of concept to assess feasibility within our deadline.

While breaking down the project into smaller tasks, I discovered two existing API(for backend, a ) we could reuse, significantly reducing the  development time since we didn't have to build it from scratch. And it also mitigate my teammate's concern for , we agreed on a plan to allocate resources efficiently and set clear milestones for progress evaluation.

**Result:** The proof of concept showed significant improvements in upload speed, and feedback from our classmates and professor was overwhelmingly positive. We successfully implemented the feature, resulting in a 30% increase in user engagement. My teammate later appreciated the collaborative approach and recognized the positive impact on our project.

#### A time u sacrificed short term interest for long term gain

----

1. (use conflict with others)
   1. my team mates think we should develop new features instead of enhancing the performance of existing feature. 

