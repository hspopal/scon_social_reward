# matching the sim/dissimilar peers with the subject  
# Author: OX 08/24/22
# run this script by first changing the participant_ID variable and then run entire the script using 
# command + shift + s on Mac 
#set wd below for mac
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
library(crayon)
incsv <- "total_socrew_scn.csv" # TOTALsocialreward.csv
all_score <- data.matrix(read.csv(incsv, sep = ','))
all_sub_ID <- read.csv(incsv, sep = ',')$record_id
all_score<- all_score[,-1]
all_score[which(all_score<3)] <- -1
all_score[which(all_score==3)] <- 0
all_score[which(all_score>3)] <- 1
participant_ID <- "SCN_181"
sub_csv <- paste("./Redcap/",participant_ID,".csv",sep="")
participant_score<- data.matrix(read.csv(sub_csv, sep = ','))
participant_score<-participant_score[,3]  
items2drop <- c(5,20,61,64,177)
participant_score[items2drop] <- 0 # remove items that are too long or salient 
participant_score_raw <-participant_score
idx_neg<-which(participant_score_raw<3)
idx_pos<-which(participant_score_raw>3)
idx_neu<-which(participant_score_raw==3)
participant_score[idx_neg] <- -1
participant_score[idx_neu] <- 0
participant_score[idx_pos] <- 1 # -1 to 1 

score_sim <- c(1:nrow(all_score))
score_dis <- c(1:nrow(all_score))
participant_score_ori <- participant_score

#################################### matching routine begins #################################### 
gen_participant_answer <- function(trials,all_score,participant_score)
{
  # utility function for extreme case when sampling from a number 
  my_sample <- function (x,num){
    y <- sample(x,num)
    if (length(x)==1&num==1)
    {
      y <- x
    }
    return(y)
  }
  
  participant_answer <- setNames(data.frame(matrix(NA, ncol = 14, nrow = max(16,max(trials)))), c("agree_pos_sim", "agree_neg_sim", "disagree_pos_sim","disagree_neg_sim",
                                                                                          "agree_pos_dis", "agree_neg_dis", "disagree_pos_dis","disagree_neg_dis",
                                                                                          "agree_pos_comp","agree_neg_comp","disagree_pos_comp","disagree_neg_comp","pos_practice","neg_practice"))
  
  ################## matching similar peer ##################
  for (i in 1:nrow(all_score))
  {
    tmp <- all_score[i,] * participant_score 
    score_sim[i] <- sum(tmp > 0, na.rm = TRUE) # find a peer with most number of agreement with the test subject 
    if (score_sim[i]==sum(abs(participant_score), na.rm = TRUE)) {
      score_sim[i] = 0 # make sure that the subject is not him/herself 
    }
  }
  sim_matched <- score_sim
  all_good <- 1
  while (all_good) # make sure having enough trials for all conditions
  {
    sim_peer_idx <- which.max(score_sim)
    sim_peer <- all_score[sim_peer_idx,]
    cnt <- 0
    # 1. peer agree positive statetment Need 24* trials agree_pos_sim
    tmp <- intersect(which(participant_score>0),which(sim_peer>0))
    random_x <- my_sample(tmp, min(agree_pos_sim,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$agree_pos_sim[1:length(random_x)] <- random_x
    }
    cnt <- cnt + length(random_x) 
    # 2. peer agree negative statement: Need 8 trials  agree_neg_sim
    tmp <- intersect(which(participant_score<0),which(sim_peer<0))
    random_x <- my_sample(tmp,  min(agree_neg_sim,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$agree_neg_sim[1:length(random_x)] <- random_x 
    }
    cnt <- cnt + length(random_x) 
    
    # 3. peer disagree positive statement Need 6 trials disagree_pos_sim
    tmp <- intersect(which(participant_score>0),which(sim_peer<0))
    random_x <- my_sample(tmp,  min(disagree_pos_sim,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$disagree_pos_sim[1:length(random_x)] <- random_x 
    }
    cnt <- cnt + length(random_x) 
    
    # 4. peer disagree negative statement Need 2 trials disagree_neg_sim
    tmp <- intersect(which(participant_score<0),which(sim_peer>0))
    random_x <- my_sample(tmp,  min(disagree_neg_sim,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$disagree_neg_sim[1:length(random_x)] <- random_x 
    }
    cnt <- cnt + length(random_x) 
    if (cnt != 32)
    {
      score_sim[sim_peer_idx]<- 0
      sim_matched[sim_peer_idx]<-cnt
      # print(paste(as.character(all_sub_ID[sim_peer_idx]), "removed from matching process"))
    }
    else
    {
      all_good<- 0
      simpeerID <- as.character(all_sub_ID[sim_peer_idx])
      print("matching successful for similar peer")
      print(paste("Similar peer is ",simpeerID))
    } # make sure we have all 32 trials
    
    if (sum(score_sim)==0) 
    { 
      print("matching failed for similar peer")
      break
    }
    
  }
  # make all used items to be 0
  participant_score[unique(participant_answer[!is.na(participant_answer)])] <- 0

  ################## matching dissimilar peer ##################
  for (i in 1:nrow(all_score))
  {
    tmp <- all_score[i,] * participant_score 
    score_dis[i] <- sum(tmp < 0, na.rm = TRUE) # find a peer with most number of disagreement with the test subject 
    if (score_dis[i]==sum(abs(participant_score), na.rm = TRUE)) {
      score_dis[i] = 0 # make sure that the subject is not him/herself 
    }
  }
  dis_matched <- score_dis
  
  all_good <- 1 # same for dissimilar peer
  while (all_good) # make sure having enough trials for all conditions
  {
    dis_peer_idx <- which.max(score_dis)
    dis_peer <- all_score[dis_peer_idx,]
    cnt <- 0
    # 5. peer agree positive statetment Need 6 trials agree_pos_dis
    tmp <- intersect(which(participant_score>0),which(dis_peer>0))
    random_x <- my_sample(tmp, min(agree_pos_dis,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$agree_pos_dis[1:length(random_x)] <- random_x
    }
    cnt <- cnt + length(random_x) 
    # 6. peer agree negative statement: Need 2 trials  agree_neg_dis
    tmp <- intersect(which(participant_score<0),which(dis_peer<0))
    random_x <- my_sample(tmp,  min(agree_neg_dis,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$agree_neg_dis[1:length(random_x)] <- random_x 
    }
    cnt <- cnt + length(random_x) 
    
    # 7. peer disagree positive statement Need 16 trials disagree_pos_sim
    tmp <- intersect(which(participant_score>0),which(dis_peer<0))
    random_x <- my_sample(tmp,  min(disagree_pos_dis,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$disagree_pos_dis[1:length(random_x)] <- random_x 
    }
    cnt <- cnt + length(random_x) 
    
    # 8. peer disagree negative statement Need 8 trials disagree_neg_sim
    tmp <- intersect(which(participant_score<0),which(dis_peer>0))
    random_x <- my_sample(tmp,  min(disagree_neg_dis,length(tmp)))
    if (length(random_x)>0)
    {
      participant_answer$disagree_neg_dis[1:length(random_x)] <- random_x 
    }
    cnt <- cnt + length(random_x) 
    if (cnt != 32)
    {
      score_dis[dis_peer_idx] <- 0
      dis_matched[dis_peer_idx]<-cnt
    #  print(paste(as.character(all_sub_ID[dis_peer_idx]), " removed from matching process"))
     # print(paste(cnt, "matches found, need 32"))
      
    } else
    {
      all_good <- 0
      dissimpeerID <- as.character(all_sub_ID[dis_peer_idx])
      print("matching successful for dissimilar peer")
      print(paste("Disimilar peer is ",dissimpeerID))
      
    } # make sure we have all 32 trials
    if (sum(score_dis)==0)
    { 
      print("matching failed for dissimilar peer")
      break
    }
  }
  # make all used items to be 0
  participant_score[unique(participant_answer[!is.na(participant_answer)])] <- 0
  # print(length(which(participant_score>0)))
  
  ################## matching computer ##################
  pos_idx<-which(participant_score>0)
  random_x <- my_sample(pos_idx, agree_pos_comp+disagree_pos_comp)
  participant_answer$agree_pos_comp[1:agree_pos_comp] <- random_x[1:agree_pos_comp]
  participant_answer$disagree_pos_comp[1:disagree_pos_comp] <- random_x[(disagree_pos_comp+1):(agree_pos_comp+disagree_pos_comp)]
  neg_idx<-which(participant_score<0)
  random_x <- my_sample(neg_idx, agree_neg_comp+disagree_neg_comp)
  participant_answer$agree_neg_comp[1:agree_neg_comp] <- random_x[1:agree_neg_comp]
  participant_answer$disagree_neg_comp[1:disagree_neg_comp] <- random_x[(agree_neg_comp+1):(agree_neg_comp+disagree_neg_comp)]
  # make all used items to be 0
  participant_score[unique(participant_answer[!is.na(participant_answer)])] <- 0
  
  # print(length(which(participant_score>0)))
  
  ################## practice ##################
  # use the rest for the practice run 
  # neg practice trials 
  neg_idx <- which(participant_score<0) # neg trials 
  random_x <- my_sample(neg_idx, neg_practice) # 5 neg items  
  if (length(random_x)>0)
  {
    participant_answer$neg_practice[1:neg_practice] <- random_x
  }
   # pos practice trials 
  pos_idx <- which(participant_score>0) # pos trials 
  random_x <- my_sample(pos_idx, pos_practice) # 3 pos items
  if (length(random_x)>0)
  {
    participant_answer$pos_practice[1:pos_practice] <- random_x
  }
  participant_score[unique(participant_answer[!is.na(participant_answer)])] <- 0
  return(participant_answer)
}
#################################### matching routine ends #################################### 

# first check if there are enough pos/neg trials
if (length(idx_pos) >= 69 & length(idx_neg) >= 35) # 69 = 66 pos items from scan and 3 from practice, 35 = 30 from scan, 5 from practice   
{
  # use hard-coded #trials per condition  
   ### similiar peer (default case)
  # 1. peer agree positive statetment
  agree_pos_sim <- 16
  # 2. peer agree negative statement
  agree_neg_sim <- 8
  # 3. peer disagree positive statement
  disagree_pos_sim <- 6
  # 4. peer disagree negative statement 
  disagree_neg_sim <- 2
  ### dissimiliar peer
  # 5. peer agree positive statetment 
  agree_pos_dis <- 6
  # 6. peer agree negative statement
  agree_neg_dis<- 2
  # 7. peer disagree positive statement 
  disagree_pos_dis <- 16
  # 8. peer disagree negative statement 
  disagree_neg_dis <- 8
  ### computer
  agree_pos_comp <- 11
  # 10. comp agree negative item
  agree_neg_comp <- 5
  # 11. comp disagree positive item
  disagree_pos_comp <- 11
  # 12. comp disagree negative item
  disagree_neg_comp <- 5
  # practice 
  # 13. pos practice item
  pos_practice <- 3
  # 14. neg item 
  neg_practice <- 5
  
  trials <- data.frame(agree_pos_sim, agree_neg_sim,disagree_pos_sim,disagree_neg_sim,
                       agree_pos_dis,agree_neg_dis,disagree_pos_dis,disagree_neg_dis,
                       agree_pos_comp,agree_neg_comp,disagree_pos_comp,disagree_neg_comp,
                       pos_practice,neg_practice)
  
  
  participant_answer <- gen_participant_answer(trials,all_score,participant_score)
  
} else ############### anomaly detected, not enough pos/neg items
{
  if (length(idx_pos) < 69)
  {
    print("Warning! Not enough positive items, use more negative items instead")
    ### calculating some numbers
    # we want to use up all pos items
    pos_ratio <- length(idx_pos)/104
    print(paste("Instead of 66.7% positive items, now matching with ", (pos_ratio*100), "% positive items",sep = ""))
  } 
  else  {
    print("Warning! Not enough negative items, use more positive items instead")
    pos_ratio <- 1 - length(idx_neg)/104
    print(paste("Instead of 66.7% positive items, now matching with ", (pos_ratio*100), "% positive items",sep = ""))
  }
    # adjust  # trials per condition accordingly  
    # similiar peer: 24 agree trials and 8 disagrer trials 
    # 1. sim peer agree positive statetment: agree_pos_sim
    agree_pos_sim <- round(24*pos_ratio)
    if (pos_ratio!=1 | pos_ratio!=0)
    {
      if (agree_pos_sim==0) {agree_pos_sim<-1}
      if (agree_pos_sim==24) {agree_pos_sim<-23}
    }  # minority trials get used at least once
    # 2. sim peer agree negative statement: agree_neg_sim
    agree_neg_sim <- 24 - agree_pos_sim
    # 3. sim peer disagree positive statement: disagree_pos_sim
    disagree_pos_sim <- round(8*pos_ratio)
    # 4. peer disagree negative statement: disagree_neg_sim
    disagree_neg_sim <- 8 - disagree_pos_sim
    # dissimiliar peer: 24 agree trials and 8 disagrer trials 
    # 5. dis peer agree positive statetment: agree_pos_dis 
    agree_pos_dis <- round(8*pos_ratio)
    # 6. dis peer agree negative statement: agree_neg_dis
    agree_neg_dis <- 8 - agree_pos_dis
    # 7. dis peer disagree positive statement: disagree_pos_dis
    disagree_pos_dis <- round(24*pos_ratio)   
    # 8. dis peer disagree negative statement:  disagree_neg_dis
    disagree_neg_dis <- 24 - disagree_pos_dis
    # computer: 16 agree, 16 disagree
    # 9. comp agree positive item: agree_pos_comp
    agree_pos_comp <- round(16 * pos_ratio)
    # 10. comp agree negative item: agree_neg_comp
    agree_neg_comp <- 16 - agree_pos_comp
    # 11. comp disagree positive item: disagree_pos_comp
    disagree_pos_comp <- round(16 * pos_ratio)
    # 12. comp disagree negative item: disagree_neg_comp
    disagree_neg_comp <- 16 - disagree_pos_comp
    # practice (may miss a trial because of aggregated rounding error)
    # 13. pos item: 8 * pos_ratio
    # how many pos items left
    pos_left <- length(idx_pos) - disagree_pos_comp - disagree_pos_sim - disagree_pos_dis - agree_pos_comp - agree_pos_dis - agree_pos_sim
    neg_left <- length(idx_neg) - disagree_neg_comp - disagree_neg_sim - disagree_neg_dis - agree_neg_comp - agree_neg_dis - agree_neg_sim
    if (length(idx_pos) < 69)
    {
      pos_practice <- min(round(8 * pos_ratio), pos_left) # make sure no rounding error
    } else
    { 
      pos_practice <- round(8 * pos_ratio) 
    }
    # 14. neg item: 8 * (1 - pos_ratio) 
    neg_practice <- min(8 - pos_practice,neg_left)
    if (length(idx_neg) < 35)
    {
      pos_practice<- 8- neg_practice
    }
  
    
    trials <- data.frame(agree_pos_sim, agree_neg_sim,disagree_pos_sim,disagree_neg_sim,
                         agree_pos_dis,agree_neg_dis,disagree_pos_dis,disagree_neg_dis,
                         agree_pos_comp,agree_neg_comp,disagree_pos_comp,disagree_neg_comp,
                         pos_practice,neg_practice)

    if (sum(trials)!=104)
    {
      print("# trials per condition does not add up")
    }
    else {
      participant_answer <- gen_participant_answer(trials,all_score,participant_score)
    }
  }



# final check   
matching_success <- 1
if (length(unique(participant_answer[!is.na(participant_answer)]))<104) # should be 96 real trials + 8 practice 
{  
  matching_success <- 0 
  print("Error: matching failed, some items are used more than once!")
}

participant_answer_pos <- participant_answer[c("agree_pos_sim","disagree_pos_sim","agree_pos_dis","disagree_pos_dis","agree_pos_comp","disagree_pos_comp","pos_practice")]
# also make sure pos items are indeed pos 
if (mean(participant_score_ori[unique(participant_answer_pos[!is.na(participant_answer_pos)])])!=1)
{
  matching_success <- 0 
  print("Error: are you sure positive items are assigned correctly")
}
# same for neg 
participant_answer_neg <- participant_answer[c("agree_neg_sim","disagree_neg_sim","agree_neg_dis","disagree_neg_dis","agree_neg_comp","disagree_neg_comp","neg_practice")]
if (mean(participant_score_ori[unique(participant_answer_neg[!is.na(participant_answer_neg)])])!=-1)
{
  matching_success <- 0 
  print("Error: are you sure negative items are assigned correctly")
}

if (matching_success==1) 
  {
    print("Matching successful. Print out the answer.")

    if (length(idx_pos) >= 69 & length(idx_neg) >= 35)
    {
      write.csv(participant_answer,paste("./Answers/",participant_ID,"_answer.csv",sep=""), row.names=FALSE)
    } else # if a insufficient pos or neg trials, need to reorganize the trials and add negative signs after moving them 
    {
      write.csv(participant_answer,paste("./Answers/",participant_ID,"_answer_ori.csv",sep=""), row.names=FALSE)
      if (length(idx_pos)<69) # too few pos items
      {
        print("Moving neg to pos columns")
        # too few positive items, move negative trials and add a negative sign
        trials2move <- 16 - trials$agree_pos_sim
        if (trials2move!=0) 
        {
        participant_answer$agree_pos_sim[(trials$agree_pos_sim+1):16] <- -1 * participant_answer$agree_neg_sim[9:(8+trials2move)]
        participant_answer$agree_neg_sim[9:(8+trials2move)] <- NA
        participant_answer$disagree_pos_dis[(trials$disagree_pos_dis+1):16] <- -1 * participant_answer$disagree_neg_dis[9:(8+trials2move)]
        participant_answer$disagree_neg_dis[9:(8+trials2move)] <- NA
        }
        trials2move <- 6 - trials$disagree_pos_sim
        if (trials2move!=0) 
        {
          participant_answer$disagree_pos_sim[(trials$disagree_pos_sim+1):6] <- -1 * participant_answer$disagree_neg_sim[3:(2+trials2move)]
          participant_answer$disagree_neg_sim[3:(2+trials2move)] <- NA
        
          participant_answer$agree_pos_dis[(trials$agree_pos_dis+1):6] <- -1 * participant_answer$agree_neg_dis[3:(2+trials2move)]
          participant_answer$agree_neg_dis[3:(2+trials2move)] <- NA
        }
        trials2move <- 11 - trials$agree_pos_comp
        if (trials2move!=0) 
        {
          participant_answer$disagree_pos_comp[(trials$disagree_pos_comp+1):11] <- -1 * participant_answer$disagree_neg_comp[6:(5+trials2move)]
          participant_answer$disagree_neg_comp[6:(5+trials2move)] <- NA
    
          participant_answer$agree_pos_comp[(trials$agree_pos_comp+1):11] <- -1 * participant_answer$agree_neg_comp[6:(5+trials2move)]
          participant_answer$agree_neg_comp[6:(5+trials2move)] <- NA
          
        }
        trials2move <- 3 - trials$pos_practice
        if (trials2move!=0) 
        {
          participant_answer$pos_practice[(trials$pos_practice+1):3] <- participant_answer$neg_practice[6:(5+trials2move)]
          participant_answer$neg_practice[6:(5+trials2move)] <- NA
        }
        # randomize so pos/neg trials order
        participant_answer$agree_pos_sim[1:16] <- sample(participant_answer$agree_pos_sim[1:16],16)
        participant_answer$disagree_pos_dis[1:16] <- sample(participant_answer$disagree_pos_dis[1:16],16)
        participant_answer$agree_pos_dis[1:6] <-sample(participant_answer$agree_pos_dis[1:6],6)
        participant_answer$disagree_pos_sim[1:6] <- sample(participant_answer$disagree_pos_sim[1:6],6)
        participant_answer$disagree_pos_comp[1:11] <- sample(participant_answer$disagree_pos_comp[1:11],11)
        participant_answer$agree_pos_comp[1:11] <- sample(participant_answer$agree_pos_comp[1:11],11)
        participant_answer$pos_practice[1:3] <- sample(participant_answer$pos_practice[1:3],3)
      } else # too few neg items 
        {
          print("Moving pos to neg columns")
          trials2move <- trials$agree_pos_sim - 16 
          if (trials2move!=0) 
          {
            participant_answer$agree_neg_sim[(trials$agree_neg_sim+1):8] <- -1 * participant_answer$agree_pos_sim[17:trials$agree_pos_sim] 
            participant_answer$agree_pos_sim[17:trials$agree_pos_sim]  <- NA
            participant_answer$disagree_neg_dis[(trials$disagree_neg_dis+1):8] <- -1 * participant_answer$disagree_pos_dis[17:trials$disagree_pos_dis] 
            participant_answer$disagree_pos_dis[17:trials$disagree_pos_dis]  <- NA
          }
          trials2move <- trials$disagree_pos_sim - 6
          if (trials2move!=0) 
          {
            participant_answer$disagree_neg_sim[(trials$disagree_neg_sim+1):2]   <- -1 * participant_answer$disagree_pos_sim[7:trials$disagree_pos_sim]
            participant_answer$disagree_pos_sim[7:trials$disagree_pos_sim] <- NA
            participant_answer$agree_neg_dis[(trials$agree_neg_dis+1):2]  <- -1 * participant_answer$agree_pos_dis[7:trials$agree_pos_dis]
            participant_answer$agree_pos_dis[7:trials$agree_pos_dis] <- NA
          }
          trials2move <- trials$agree_pos_comp - 11
          if (trials2move!=0) 
          {
            participant_answer$disagree_neg_comp[(trials$disagree_neg_comp+1):11] <- -1 * participant_answer$disagree_pos_comp[12:(11+trials2move)]
            participant_answer$disagree_pos_comp[11:(11+trials2move)] <- NA
            participant_answer$agree_neg_comp[(trials$agree_neg_comp+1):11] <- -1 * participant_answer$agree_pos_comp[12:(11+trials2move)]
            participant_answer$agree_pos_comp[11:(11+trials2move)] <- NA
          }
          trials2move <- trials$pos_practice - 3 
          if (trials2move!=0) 
          {
            participant_answer$neg_practice[(trials$neg_practice+1):5] <- -1* participant_answer$pos_practice[4:trials$pos_practice]
            participant_answer$pos_practice[4:trials$pos_practice] <- NA
          }
          # randomize so pos/neg trials order
          participant_answer$agree_neg_sim[1:8] <- sample(participant_answer$agree_neg_sim[1:8],8)
          participant_answer$disagree_neg_dis[1:8] <- sample(participant_answer$disagree_neg_dis[1:8],8)
          participant_answer$agree_neg_dis[1:2] <-sample(participant_answer$agree_neg_dis[1:2],2)
          participant_answer$disagree_neg_sim[1:2] <- sample(participant_answer$disagree_neg_sim[1:2],2)
          participant_answer$disagree_neg_comp[1:11] <- sample(participant_answer$disagree_neg_comp[1:11],11)
          participant_answer$agree_neg_comp[1:11] <- sample(participant_answer$agree_neg_comp[1:11],11)
          participant_answer$neg_practice[1:5] <- sample(participant_answer$neg_practice[1:5],5)
        }
      write.csv(participant_answer[1:16,],paste("./Answers/",participant_ID,"_answer.csv",sep=""), row.names=FALSE)
      cat(red("Insufficient pos/neg items!\n"))
      cat(red(paste("Compare ", participant_ID,"_answer_ori.csv with ", participant_ID,"_answer.csv!\n",sep = "")))
    } 
} else {
    print("Matching failed. See error msg, no answer was printed!")
  }
# to check #trial per condition  
colSums(!is.na(participant_answer))

# n_occur <-  data.frame(table(unlist(participant_answer,use.names=FALSE) ))
