# matching the sim/dissimilar peers with the test subject  
#set wd below for mac
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
#set wd below for pc
setwd("D:/SocialReward/Stimuli_SocialReward")
incsv <- "total_socrew_scn.csv" # TOTALsocialreward.csv
#incsv <- "TOTALsocialreward.csv" # if matching fails switch to this one
all_score <- data.matrix(read.csv(incsv, sep = ','))
all_sub_ID <- read.csv(incsv, sep = ',')$record_id
all_score<- all_score[,-1]
all_score[which(all_score<3)] <- -1
all_score[which(all_score==3)] <- 0
all_score[which(all_score>3)] <- 1
participant_ID <- "SCN_144"
sub_csv <- paste("./Redcap/",participant_ID,".csv",sep="")
participant_score<- data.matrix(read.csv(sub_csv, sep = ','))
participant_score<-participant_score[,3]  
participant_score_raw <-participant_score - 3 # -2 to 2
participant_score[which(participant_score<3)] <- -1
participant_score[which(participant_score==3)] <- 0
participant_score[which(participant_score>3)] <- 1 # -1 to 1 
items2drop <- c(5,20,61,64,177)
participant_score[items2drop] <- 0 # remove items that are too long or salient 
score_sim <- c(1:nrow(all_score))
score_dis <- c(1:nrow(all_score))

for (i in 1:nrow(all_score))
{
  tmp <- all_score[i,] * participant_score 
  score_sim[i] <- sum(tmp > 0, na.rm = TRUE) # find a peer with most number of agreement with the test subject 
  if (score_sim[i]==sum(abs(participant_score))) {
    score_sim[i] = 0 # make sure that the subject does not him/herself 
  }
}
participant_answer <- setNames(data.frame(matrix(NA, ncol = 14, nrow = 16)), c("agree_pos_sim", "agree_neg_sim", "disagree_pos_sim","disagree_neg_sim",
                                                                               "agree_pos_dis", "agree_neg_dis", "disagree_pos_dis","disagree_neg_dis",
                                                                               "agree_pos_comp","agree_neg_comp","disagree_pos_comp","disagree_neg_comp","pos_practice","neg_practice"))
# similiar peer
# 1. peer agree positive statetment Need 16 trials agree_pos_sim
# 2. peer agree negative statement: Need 8 trials  agree_neg_sim
# 3. peer disagree positive statement Need 6 trials disagree_pos_sim
# 4. peer disagree negative statement Need 2 trials disagree_neg_sim
# dissimiliar peer
# 5. peer agree positive statetment Need 6 trials agree_pos_dis
# 6. peer agree negative statement: Need 2 trials  agree_neg_dis
# 7. peer disagree positive statement Need 16 trials disagree_pos_dis
# 8. peer disagree negative statement Need 8 trials disagree_neg_dis
# computer
# 9. comp positive item
# 10. comp negative item
all_good <- 1
while (all_good) # make sure having enough trials for all conditions
{
  sim_peer_idx <- which.max(score_sim)
  sim_peer <- all_score[sim_peer_idx,]
  cnt <- 0
  # 1. peer agree positive statetment Need 16 trials agree_pos_sim
  tmp <- intersect(which(participant_score>0),which(sim_peer>0))
  random_x <- sample(tmp, min(16,length(tmp)))
  cnt <- cnt + length(random_x) 
  participant_answer$agree_pos_sim[1:length(random_x)] <- random_x
  # 2. peer agree negative statement: Need 8 trials  agree_neg_sim
  tmp <- intersect(which(participant_score<0),which(sim_peer<0))
  random_x <- sample(tmp,  min(8,length(tmp)))
  participant_answer$agree_neg_sim[1:length(random_x)] <- random_x 
  cnt <- cnt + length(random_x) 
  
  # 3. peer disagree positive statement Need 6 trials disagree_pos_sim
  tmp <- intersect(which(participant_score>0),which(sim_peer<0))
  random_x <- sample(tmp,  min(6,length(tmp)))
  if (length(random_x)>0)
  {
    participant_answer$disagree_pos_sim[1:length(random_x)] <- random_x 
  }
  cnt <- cnt + length(random_x) 
  
  # 4. peer disagree negative statement Need 2 trials disagree_neg_sim
  tmp <- intersect(which(participant_score<0),which(sim_peer>0))
  random_x <- sample(tmp,  min(2,length(tmp)))
  if (length(random_x)>0)
  {
  participant_answer$disagree_neg_sim[1:length(random_x)] <- random_x 
  }
  cnt <- cnt + length(random_x) 
  if (cnt != 32)
  {
    score_sim[sim_peer_idx]<- 0
  }
  else
  {
    all_good<- 0
    simpeerID <- as.character(all_sub_ID[sim_peer_idx])
  } # make sure we have all 32 trials
}

all_score[,unique(participant_answer[!is.na(participant_answer)])] <- 0 # remove items that have been used before matching the dissimilar peer
for (i in 1:nrow(all_score))
{
  tmp <- all_score[i,] * participant_score 
  # score_sim[i] <- sum(tmp > 0, na.rm = TRUE) # find a peer with most number of agreement with the test subject 
  score_dis[i] <- sum(tmp < 0, na.rm = TRUE) # find a peer with most number of disagreement with the test subject 
}

all_good <- 1 # same for dissimilar peer
while (all_good) # make sure having enough trials for all conditions
{
  dis_peer_idx <- which.max(score_dis)
  dis_peer <- all_score[dis_peer_idx,]
  cnt <- 0
  # 5. peer agree positive statetment Need 6 trials agree_pos_dis
  tmp <- intersect(which(participant_score>0),which(dis_peer>0))
  random_x <- sample(tmp, min(6,length(tmp)))
  if (length(random_x)>0)
  {
    participant_answer$agree_pos_dis[1:length(random_x)] <- random_x
  }
  cnt <- cnt + length(random_x) 
  # 6. peer agree negative statement: Need 2 trials  agree_neg_sim
  tmp <- intersect(which(participant_score<0),which(dis_peer<0))
  random_x <- sample(tmp,  min(2,length(tmp)))
  if (length(random_x)>0)
  {
    participant_answer$agree_neg_dis[1:length(random_x)] <- random_x 
  }
  cnt <- cnt + length(random_x) 
  
  # 7. peer disagree positive statement Need 16 trials disagree_pos_sim
  tmp <- intersect(which(participant_score>0),which(dis_peer<0))
  random_x <- sample(tmp,  min(16,length(tmp)))
  participant_answer$disagree_pos_dis[1:length(random_x)] <- random_x 
  cnt <- cnt + length(random_x) 
  
  # 8. peer disagree negative statement Need 8 trials disagree_neg_sim
  tmp <- intersect(which(participant_score<0),which(dis_peer>0))
  random_x <- sample(tmp,  min(8,length(tmp)))
  participant_answer$disagree_neg_dis[1:length(random_x)] <- random_x 
  cnt <- cnt + length(random_x) 
  if (cnt != 32)
  {
    score_sim[dis_peer_idx]<- 0
  }
  else{
   all_good<- 0
   dissimpeerID <- as.character(all_sub_ID[dis_peer_idx])
  } # make sure we have all 32 trials
}

# make all used items to be 0
#  "agree_pos_comp" = 11,"agree_neg_comp"=5,"disagree_pos_comp"=11,"disagree_neg_comp"=5,
participant_score[unique(participant_answer[!is.na(participant_answer)])] <- 0
tmp_neg <- which(participant_score<0)
tmp_pos <- which(participant_score>0)
n1 <- length(tmp_pos) 
n2 <- length(tmp_neg)
if (n1 > 22 & n2 > 10)
{
  random_x <- sample(tmp_pos, 22)
  participant_answer$agree_pos_comp[1:11] <- random_x[1:11]
  participant_answer$disagree_pos_comp[1:11] <- random_x[12:22]
  random_x <- sample(tmp_neg, 10)
  participant_answer$agree_neg_comp[1:5] <- random_x[1:5]
  participant_answer$disagree_neg_comp[1:5] <- random_x[6:10]
} else {print("not enough trials for computer, adjust manually")}

# use the rest for the practice run 
participant_score[unique(participant_answer[!is.na(participant_answer)])] <- 0
tmp <- which(participant_score<0)
random_x <- sample(tmp, 5)
participant_answer$neg_practice[1:length(random_x)] <- random_x
tmp <- which(participant_score>0)
random_x <- sample(tmp, 3)
participant_answer$pos_practice[1:length(random_x)] <- random_x
if (length(unique(participant_answer[!is.na(participant_answer)])) ==104) # should be 96 real trials + 8 practice 
{
  print("matching successful")
  print(paste("Similar peer is",simpeerID,". Dissimilar peer is ", dissimpeerID))
  write.csv(participant_answer,paste("./Answers/",participant_ID,"_answer.csv",sep=""), row.names=FALSE)
} else {
  print("matching failed")
}
  
