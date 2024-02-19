setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
timing <- read.csv("SocialConnection_Master.csv", sep = ',')
timing1 <- as.matrix(timing[1:120,5:6])
mean_diff <- 10
while (mean_diff > .05)
{
  sid <- sample(120)
  cnt <- 1
  mean_t <- c(1:5)
  for (i in c(1:5))
  {
    sid0 <- sid[cnt:(cnt+23)]
    mean_t[i] <- mean(timing1[sid0,])
    cnt <- cnt + 24
  }
  mean_diff<-max(mean_t)-min(mean_t)
}
timing2<-timing1[sid,]
write.csv(timing2,file = "out.csv")
