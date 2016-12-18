# Initial Planning Document for the Alexa Prize
 This document is for planning for the Alexa prize.
 
 ## Major Tasks
 1. Reading (Core Team) -- make a reading.md
    -  IRL
    -  NLP Reading (ask John).
    -  Text Embedding
    -  Conversational AI
        -  Generative Models for Conversation
        -  BaBi Datasets (etc)
    -  Memory augmented neural networks
        -  Document Retrieval
        -  Entity Neural Networks
        -  DNC
  2. Symbolic version/baseline fallbackmethod
    - Implement an [AIML](http://www.alicebot.org/aiml.html) mark up corpus for the following categories:
        a. Entertainment
        b. Fashion
        c. Politics
        d. Sports
        e. Technology
        *. Sub categories.
    - Connect the A.L.I.C.E. system to ALEXA.
  3. Get huge corpus of conversation data and clean it. 
  4. Reevaluate proposal after reading the state of the art. 
  5. Implement baseline system proposed in document (eowb)
  6. Find a way to default back to the symbolic baseline
  7. Make a design for AWS/Lambda/"Neural Server."
  8. Get money from John.
  



## Ideas
1. Standard Proposal..
2. Have a generative model for AIML learnt from existing conversation corpi. Then make huge database of AIML, embed the question into a space 
   and embed the AIML database into the space, compare distance; generate response.
3. RL^2 version of Standard Proposal.
 
    
