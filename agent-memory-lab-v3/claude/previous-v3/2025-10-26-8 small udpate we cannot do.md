cursor有三种mode by default we use "Agent" mode (the other two: Plan and Ask) - 这个是user query level 而不是session
  level。每一个user query用的mode可能不同。怎么设计这个部分？不要太复杂 目前default都是"agent" mode。this is a small update,
  right? 这个在数据结构中也记得更新下


  看了一下export chat不支持输出的mode、也不会记录tokens等。等待cursor今后发布更新吧