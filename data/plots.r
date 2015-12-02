# read in the data
# timesteps vary between 150 (0-149) and 151 (0-150); best to truncate all to 150 quarters
# set working directory if necessary e.g. setwd('~/Desktop/.')
dat <- read.table("gpes_fromlog.csv", header=FALSE, skip=1, sep=",", col.names = c("trait", "timestep", "t1", "t2", "t3", "total"))

# find traits with high slope at end
traits <- unique(dat[,1])
zz <- vector(mode="numeric", length=length(traits))
for( i in 1:length(traits)) {
  xx <- tail(dat[dat[,1]==traits[i], 3],30)         # last 30 t1 values for trait[i]
  zz[i] <- mean(tail(xx, n=5)) - mean(head(xx, n=5))   # "slope" over last 30 data pts
}

# extract the traits
traits[zz>.002]             
hottraits <- c("bone",
               "implant",
               "medic",
               "instrument",
               "spinal",
               "needl",
               "patient")
dates <- seq(as.Date("04/01/1978", format = "%d/%m/%Y"), by = "3 months", length = length(dat[dat[,1]=="there", 2]))
# OLD: plot(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3],
plot(dates, dat[dat[,1]=="there", 3],
        type="n", ylab="cov(Ca,Xa)", xlab="Year (sampled quarterly)", ylim=c(-0.001,0.01),
        main="hot traits", col.main="green",
        sub="bone, implant, medic, instrument, spinal, needl, patient", col.sub="green")

legend("topleft", inset = 0, title = "Legend Title", legend= c(1:3), fill = c(1:7), horiz=FALSE)

for( i in 1:length(hottraits) ) {
  lines(dates, dat[dat[,1]==hottraits[i], 3], col="green", lwd=4)
  #OLD lines(dat[dat[,1]=="there", 2], dat[dat[,1]==hottraits[i], 3], col="green", lwd=4)
}

####################################
# Alex quick mockup of binned by year results:
###############
run1 <- "gpe_tfidf_year_run1.csv" # not sure what years it went from 1978->2015?
run2 <- "gpe_tfidf_year_run2.csv" # run2 went from 1976 to 2012
dat <- read.table(run2, header=TRUE, sep=",")
dates <- seq(as.Date("04/01/1976", format = "%d/%m/%Y"), by = "year", length = length(dat[dat[,1]=="internet", 2]))

traits <- c("bone",
               "implant",
               "medic",
               "instrument",
               "spinal",
               "needl",
               "patient")
for( i in 1:length(traits) ) {
  fn <- paste(traits[i], ".pdf", sep="")
  title <- paste(traits[i], " binned by year")
  pdf(fn)
  
  plot(dates, dat[dat[,1]=="internet", 3],
       type="n", ylab="Value", xlab="Year (sampled yearly)", ylim=c(-0.001,0.01),
       main=title, col.main="black",
       sub="", col.sub="green")
  
  legend("topleft", inset = 0, title = "Curves", 
         legend= c("t1", "t2", "t3", "tot", expression(bar(X^a)), expression(bar(X[d])), "muts"),
         fill = c("green","blue","red","purple", "orange", "pink","violet"), horiz=FALSE)
  
  
  lines(dates, dat[dat[,1]==traits[i], 3], col="green", lwd=4)
  lines(dates, dat[dat[,1]==traits[i], 4], col="blue", lwd=4)
  lines(dates, dat[dat[,1]==traits[i], 5], col="red", lwd=4)
  lines(dates, dat[dat[,1]==traits[i], 6], col="purple", lwd=4)
  lines(dates, dat[dat[,1]==traits[i], 9], col="orange", lwd=4)
  lines(dates, dat[dat[,1]==traits[i], 10], col="pink", lwd=4)
  # lines(dates, dat[dat[,1]==traits[i], 11], col="violet", lwd=4) doesn't show up.
  dev.off()
}


####################################

maxx <- max(dat[,3:6])
minn <- min(dat[,3:6])
plot(dat[1:151,2],dat[1:151,3], type="l", ylim=c(maxx,minn))

dat[303:(303+150), 2:3] # polypeptide
plot(dat[303:(303+150), 2],dat[303:(303+150), 3], type="l", ylim=c(maxx,minn))

dat[102240:(102240+149), 2:3] # internet
plot(dat[102240:(102240+149), 2],dat[102240:(102240+149), 3], type="l")

# subset dat: only time step 0 (for each trait)
dat[dat[,2]==0,]

# only rows of data for trait "internet"; yields a 150x6 matrix
dat[dat[,1]=="internet",]     # matrix of all values for trait "internet"
dat[dat[,1]=="internet", 2]   # vector of times for trait "internet"
dat[dat[,1]=="internet", 3]   # vector of t1 values for trait "internet"
dat[dat[,1]=="internet", 4]   # vector of t2 values for trait "internet"
dat[dat[,1]=="internet", 5]   # vector of t3 values for trait "internet"
dat[dat[,1]=="internet", 6]   # vector of total values for trait "internet"

# plot t1 time series for trait "internet" (ditto for t2, t3, total)
plot(dat[dat[,1]=="internet", 2], dat[dat[,1]=="internet", 3], 
     type="l", main="internet", ylab="cov(Ca,Xa)", xlab="quarter")

plot(dat[dat[,1]=="web", 2], dat[dat[,1]=="web", 3], 
     type="l", main="web", ylab="cov(Ca,Xa)", xlab="quarter")

# plot time series of t1 for trait = <input character string>
# assume trait is a character string tf-idf stems

plottrait <- function (trait, ...) {
  plot(dat[dat[,1]==trait, 2], 
      dat[dat[,1]==trait, 3], 
      main=trait, 
      type="l", ylab="cov(Ca,Xa)", xlab="quarter", ...)
}

plottrait("internet")
plottrait("host")


# plot smoothed time series for trait (input character string)
# using default smoother
plotsmoothtrait <- function (trait,...) {
  plot(dat[dat[,1]==trait, 2], 
       smooth(dat[dat[,1]==trait, 3]), 
       main=trait, 
       type="l", ylab="cov(Ca,Xa)", xlab="quarter",...)
}

plot2smoothtrait <- function (trait,...) {
  plot(dat[dat[,1]==trait, 2], 
       smooth(smooth(dat[dat[,1]==trait, 3])), 
       main=trait, 
       type="l", ylab="cov(Ca,Xa)", xlab="quarter",...)
}

plotsmoothtrait("network")
plot2smoothtrait("network")

# fix ylim to some reference value
plotsmoothtrait <- function (trait,...) {
  plot(dat[dat[,1]==trait, 2], 
       smooth(dat[dat[,1]==trait, 3]), 
       main=trait, 
       type="l", ylab="cov(Ca,Xa)", xlab="quarter",...)
}


#########################################################################
# max of stop words = 0.003674169
# min of stop words = -0.002436793
max(dat[dat[,1]=="there",        3],
    dat[dat[,1]=="the",          3],
    dat[dat[,1]=="configur",     3],
    dat[dat[,1]=="first",        3],
    dat[dat[,1]=="second",       3],
    dat[dat[,1]=="one",          3],
    dat[dat[,1]=="two",          3],
    dat[dat[,1]=="three",        3],
    dat[dat[,1]=="some",         3],
    dat[dat[,1]=="can",          3]
)

# plot stop words
traits <- c("there",
            "the",
            "configur",
            "one",
            "two",
            "three",
            "some",
            "can")

########### work in progress ##############################
########### generalizing max and min calculations #########
tmp <- vector(mode="numeric", length=length(traits))
for( i in 1:length(traits) ) {
  tmp[i] <- max(dat[dat[,1]==traits[i], 3])
}
max(tmp)
########## end work in progress ##########################

plot(dat[dat[,1]==traits[i], 2], dat[dat[,1]==traits[i], 3],
     type="n", ylab="cov(Ca,Xa)", xlab="quarter", ylim=c(-0.004,0.01),
     main="stop words", col.main="gray",
     sub="there, the, configur, one, two, three, some, can", col.sub="gray")
for( i in 1:length(traits) ) {
  lines(dat[dat[,1]==traits[i], 2], dat[dat[,1]==traits[i], 3], col="gray", lwd=4)
}

##########################################################################
# max of material traits = 0.01714779
# min of material traits = -0.003525992
max(dat[dat[,1]=="bone",    3],
    dat[dat[,1]=="acid",    3],
    dat[dat[,1]=="air",     3],
    dat[dat[,1]=="dye",     3],
#    dat[dat[,1]=="glass",   3],
    dat[dat[,1]=="oil",     3],
    dat[dat[,1]=="plastic", 3],
    dat[dat[,1]=="resin",   3],
    dat[dat[,1]=="salt",    3],
    dat[dat[,1]=="water",   3]
)

# plot material traits
traits <- c("ink",
            "dye",
            "glass",
            "oil",
            "plastic",
            "resin",
            "salt", 
            "water")
plot(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3],
     type="n", ylab="cov(Ca,Xa)", xlab="quarter", ylim=c(-0.004,0.01),
     main="material traits", col.main="blue",
     sub="there, the, configur, one, two, three, some, can", col.sub="blue")
for( i in 1:length(traits) ) {
  lines(dat[dat[,1]==traits[i], 2], dat[dat[,1]==traits[i], 3], col="blue", lwd=4)
}


############################################################################
# max of internet traits = 0.006450918
# min of internet traits = -0.0006435661
max(dat[dat[,1]=="internet",    3],
    dat[dat[,1]=="hyperlink",   3],
    dat[dat[,1]=="broadband",   3],
    dat[dat[,1]=="client",      3],
    dat[dat[,1]=="server",      3],
    dat[dat[,1]=="metadata",    3],
    dat[dat[,1]=="site",        3],
    dat[dat[,1]=="web",         3],
    dat[dat[,1]=="multimedia",  3],
    dat[dat[,1]=="host",        3]
)

# plot internet traits
plot(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3],
     type="n", ylab="cov(Ca,Xa)", xlab="quarter", ylim=c(-0.004,0.01),
     main="internet traits", col.main="red",
     sub="internet, client, server, site, web, multimedia, host", col.sub="red")
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="internet", 3], col="red", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="hyperlink", 3], col="red", lwd=4) # too flat
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="broadband", 3], col="red", lwd=4) # too flat
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="client", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="server", 3], col="red", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="metadata", 3], col="red", lwd=4) # wrong length
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="site", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="web", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="multimedia", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="host", 3], col="red", lwd=4)
############################################################################
# max of machine traits = 0.001648519
# min of machine traits = -0.003700962
max(dat[dat[,1]=="arm",        3],
    dat[dat[,1]=="blade",      3],
    dat[dat[,1]=="bolt",       3],
    dat[dat[,1]=="bracket",    3],
    dat[dat[,1]=="brake",      3],
    dat[dat[,1]=="brush",      3],
    dat[dat[,1]=="cap",        3],
    dat[dat[,1]=="chamber",    3],
    dat[dat[,1]=="clamp",      3],
    dat[dat[,1]=="cover",      3],
    dat[dat[,1]=="drum",      3]
)

# plot machine traits
plot(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3],
     type="n", ylab="cov(Ca,Xa)", xlab="quarter", ylim=c(-0.004,0.01),
     main="machine traits", col.main="purple",
     sub="arm, blade, bolt, bracket, brush, cap, chamber, clamp, cover, drum", col.sub="purple")
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="arm", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="blade", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="bolt", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="bracket", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="brush", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="cap", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="chamber", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="clamp", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="cover", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="drum", 3], col="purple", lwd=4)

############################################################################
# max of IT traits = 0.009742352
# min of IT traits =  -0.00296077
min(dat[dat[,1]=="comput",           3],
    dat[dat[,1]=="cpu",              3],
    dat[dat[,1]=="databas",          3],
    dat[dat[,1]=="data",             3],
    dat[dat[,1]=="gps",              3],
    dat[dat[,1]=="network",          3],
    dat[dat[,1]=="remote",           3],
    dat[dat[,1]=="semiconductor",    3],
    dat[dat[,1]=="software",         3],
    dat[dat[,1]=="spreadsheet",      3]
)

# plot IT traits
plot(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3],
     type="n", ylab="cov(Ca,Xa)", xlab="quarter", ylim=c(-0.004,0.01),
     main="IT traits",col.main="orange",
     sub="comput, databas, data, gps, network, software", col.sub="orange")
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="comput", 3], col="orange", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="databas", 3], col="orange", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="data", 3], col="orange", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="gps", 3], col="orange", lwd=4)             # too low
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="network", 3], col="orange", lwd=4)
lines(dat[dat[,1]=="software", 2], dat[dat[,1]=="software", 3], col="orange", lwd=4)      # wrong length
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="remote", 3], col="orange", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="semiconductor", 3], col="orange", lwd=4) # wrong length
# lines(dat[dat[,1]=="spreadsheet", 2], dat[dat[,1]=="spreadsheet", 3], col="orange", lwd=4)   # too low
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="cpu", 3], col="orange", lwd=4)           # too low


###################################################################
# plot all traits together
plot(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3],
     type="n", ylab="cov(Ca,Xa)", xlab="quarter", ylim=c(-0.004,0.01),
     main="differential splitting (term 1)",
     sub="stop:gray IT:orange internet:red machine:purple material:blue")

lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="comput", 3], col="orange", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="cpu", 3], col="orange", lwd=4)           # too low
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="databas", 3], col="orange", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="data", 3], col="orange", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="gps", 3], col="orange", lwd=4)             # too low
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="network", 3], col="orange", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="remote", 3], col="orange", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="semiconductor", 3], col="orange", lwd=4) # wrong length
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="software", 3], col="orange", lwd=4)

lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="internet", 3], col="red", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="hyperlink", 3], col="red", lwd=4) # too flat
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="broadband", 3], col="red", lwd=4) # too flat
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="client", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="server", 3], col="red", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="metadata", 3], col="red", lwd=4) # wrong length
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="site", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="web", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="multimedia", 3], col="red", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="host", 3], col="red", lwd=4)

lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="arm", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="blade", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="bolt", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="bracket", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="brush", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="cap", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="chamber", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="clamp", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="cover", 3], col="purple", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="drum", 3], col="purple", lwd=4)

lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="ink", 3], col="blue", lwd=4)
# lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="acid", 3], col="blue", lwd=4) # data glitch at start
# lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="air", 3], col="blue", lwd=4)
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="dye", 3], col="blue", lwd=4)
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="glass", 3], col="blue", lwd=4) # length different
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="oil", 3], col="blue", lwd=4)
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="plastic", 3], col="blue", lwd=4)
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="resin", 3], col="blue", lwd=4)
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="salt", 3], col="blue", lwd=4)
lines(dat[dat[,1]=="bone", 2], dat[dat[,1]=="water", 3], col="blue", lwd=4)

lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="there", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="the", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="configur", 3], col="gray", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="first", 3], col="gray", lwd=4)
# lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="second", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="one", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="two", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="three", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="some", 3], col="gray", lwd=4)
lines(dat[dat[,1]=="there", 2], dat[dat[,1]=="can", 3], col="gray", lwd=4)

