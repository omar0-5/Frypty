


1- how will we read the sentence 
    A- the first word time and the last word time 
    B- each word has a start and end time 

    by using B we can skip human speaking errors 
    EX: rev revinue 

2- how will we make the start and end time for words the code cant handle like numbers
    
    we will bound each missing word with a left and right bound , 
    if there is multiple missing words consecvtily we will split the time evenly ,
    this is not optimal but for our use case it will simplify future implementation