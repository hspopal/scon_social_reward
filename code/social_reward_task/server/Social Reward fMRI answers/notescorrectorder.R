library(dplyr)
#set below wd for mac
#setwd("/Volumes/research$/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/Notes")
#set below wd for PC
setwd("U:/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/Notes")
df <- read.csv("SCNnotes.csv")
Split_based_on_group <- split(df, with(df, interaction(whichissim)), drop = TRUE)
peer1sim <- Split_based_on_group[[1]]
peer2sim <- Split_based_on_group[[2]]
peer1sim <- peer1sim[-c(2)]
peer2sim <- peer2sim[-c(2)]
col_order <- c("record_id","note2","contact2","note1","contact1","simpeerid","dispeerid")
order2 <- peer2sim[,col_order]

colnames(peer1sim) <- c("record_id","similar_note","contactforsim","dissimilar_note","contactfordis","simpeerid","dispeerid")

colnames(order2) <- c("record_id","similar_note","contactforsim","dissimilar_note","contactfordis","simpeerid","dispeerid")

combine <- rbind(peer1sim,order2)
#set below for mac
#write.csv(combine,'/Volumes/research$/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/Notes/notescorrectorder.csv', row.names = FALSE)
#set below for PC
write.csv(combine,'U:/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/Notes/notescorrectorder.csv', row.names = FALSE)
