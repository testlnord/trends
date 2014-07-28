library("zoo")
library("lattice")
library("xts")
library("mvtsplot")
library("forecast")
# working with ajax data
# its plots looks the best

tsnorm <- function(tser){
  a <- min(tser)
  b <- max(tser)
  (tser - a)/(b - a)
}
tech_names = c(".net", "ajax", "angularjs", "android")
par(mfrow=c(4,2))
process_and_plot <- function(tech_name){               
  ts.wiki <- read.zoo(paste("../data/wiki/", tech_name, "/r_data.txt", sep= ""), sep = "|", format="%d %b %Y")
  ts.google <- read.zoo(paste("../data/google/", tech_name, "/r_data.txt", sep= ""), sep = "|", format="%d %b %Y")
  #ts.sot <- read.zoo(paste("../data/sot/", tech_name, "/r_data.txt", sep= ""), sep = "|", format="%d %b %Y")
  ts.itjobs <- read.zoo(paste("../data/itjobs/", tech_name, "/r_data.txt", sep= ""), sep = "|", format="%d %b %Y")
  
  cols <- c('yellow', 'red', 'green')
  
  ts.all <- list(ts.wiki, ts.google, ts.itjobs)
  #ts.all <- mapply( function(t) period.apply(x=t, endpoints(t, 'months', k=1), FUN=sum), ts.all)
  # weekly
  #ts.all <- mapply(aggregate, ts.all, MoreArgs = list(by = function(d) as.Date(paste(format(d, "%Y-%U"), "1"), format="%Y-%U %u")))
  # monthly
  ts.all <- mapply(aggregate, ts.all, MoreArgs = list(by = function(d) as.Date(paste(format(d, "%Y-%m"), "1"), format="%Y-%m %d")))
  latest.start <- max(do.call(c, mapply(start ,ts.all, SIMPLIFY = FALSE)))
  
  ts.all <- mapply(window, ts.all, MoreArgs = list(start=latest.start))
  
  ts.all.norm <- mapply(tsnorm, ts.all)
  
  par(pch=20, col="blue") # plotting symbol and color
  plot(ts.all.norm[[1]], type='p', col=cols[1], ylab = tech_name, xlab ="")
  mapply(function(dat, c) points(dat, col=c), ts.all.norm[-1], cols[-1])
  
  mapply(function(dat, c) lines(dat, col=c, lwd=3), mapply(rollmean,ts.all.norm, MoreArgs = list(k=11)), cols)
  #lines(ts.google)
  #lines(ts.sot)
  #lines(ts.itjobs)
  m <- do.call(merge, ts.all.norm)
  colnames(m) <- c("wiki", "google", "itj")
  m.mean = (m$wiki + m$google + m$itj)/3
  points(m.mean, col='black', lwd=5, pch=19)
  lines(rollmean(m.mean, k = 11), col='black', lwd=5)
  #mvtsplot(as.matrix(coredata(m)), levels=10, norm="internal", rowstat = "mean")
  m.forecast = forecast(na.approx(as.ts(m.mean)), 100)
  plot(m.forecast)
}
for (name in tech_names) process_and_plot(name)
par(mfrow=c(1,1))