#set wd below for mac
#setwd("/Volumes/research$/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/wide_answers")
#set wd below for pc
setwd("U:/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/wide_answers")
olddata_wide <- read.csv("SCN_222.csv")
library(tidyr)

library(data.table)
colnames(olddata_wide)[1] <- "record_id"
olddata_wide <- olddata_wide[,-2]
long <- melt(setDT(olddata_wide), id.vars = c("record_id"), variable.name = "item")

#erase open-ended questions if they are at the end
new_long<- long[-c(212:219), ]

#for mac
#write.csv(new_long,'/Volumes/research$/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/testeli.csv', row.names = FALSE)
#for pc
write.csv(new_long,'U:/redcay/DSCN Lab/Experiments/SCONN/Social Reward fMRI answers/SCN_222.csv', row.names = FALSE)
