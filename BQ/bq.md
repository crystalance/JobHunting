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

//

```java

// elevator

class elevatorController{
  
  int curlevel;
  
  Map<Signal, Integer> map;
  
  public elevatorController(){
    curlevel=1;
    map.put(signal, Integer);
  }
  void acceptRequst(Signal sig){
    // direct 0 down
    // 1 up
    int direct = map.get(sig);
   if(curlevel==1{
     if(direct==1){
       curlevel++;
     }else{
      return;
     }
   }else if(curlevel==2){
       if(direct==0){
      curlevel--;
     }else if(){
       curlevel++;
     }
   }else{
       if(direct==3){
       curlevel--;
     }else{
       return;
     }
   }
  
  }
  
}



```

