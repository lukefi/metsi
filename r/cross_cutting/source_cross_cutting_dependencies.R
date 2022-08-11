# this file initialises variables and functions used by r/cross_cutting/cross_cutting_main.R and should be sourced before running it
source("./r/cross_cutting/ApteerausNasberg.R")
source("./r/cross_cutting/Runkokayraennusteet.R")
source("./r/cross_cutting/Tilavuus.R")
source("./r/cross_cutting/Runkokayran korjausmalli.R")
source("./r/cross_cutting/Korjauskertoimet.R")


taper_curve_list <- list("birch" = readRDS(file.path("./r/cross_cutting/taper_curves/birch.rds")),
                         "pine" = readRDS(file.path("./r/cross_cutting/taper_curves/pine.rds")),
                         "spruce" = readRDS(file.path("./r/cross_cutting/taper_curves/spruce.rds")))

timber_grades_table <- read.table("./r/cross_cutting/Puutavaralajimaarittelyt.txt")
