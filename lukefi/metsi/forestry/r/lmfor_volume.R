library_requirements <- c("lmfor")
if(!all(library_requirements %in% installed.packages()[, "Package"]))
  install.packages(repos="https://cran.r-project.org", dependencies=TRUE, library_requirements)
library(lmfor)

# test <- data.frame(
#   height = c(10.3, 14.7),
#   breast_height_diameter = c(25.3, 32.3),
#   degree_days = c(400.3, 400.3),
#   species = c("pine", "spruce"),
#   model_type = c("climbed", "climbed")
# )

known_species <- c("birch", "pine", "spruce")
known_model_types <- c("climbed", "felled", "scanned")

has_species <- function(tree_data, species) {
  any(tree_data$species == species)
}

computable_dataframe <- function(tree_data) {
  data.frame(
    h = tree_data$height,
    dbh = tree_data$breast_height_diameter,
    temp_sum = tree_data$degree_days,
    species = factor(tree_data$species, levels = known_species),
    dataset = factor(tree_data$model_type, levels = known_model_types)
  )
}

volumes_for_species <- function(prepared_data, species, volmods) {
  # Need to do explicit check for existence of specific species
  # predvff raises an Error with empty data.
  # Maybe handle with tryCatch instead?
  if (has_species(prepared_data, species)) {
    attr(predvff(prepared_data[prepared_data$species == species,], get(species, volmods$model3)), "trees")$volume
  }
  else {
    vector()
  }
}

compute_tree_volumes <- function(tree_data, volmods_file) {
  volmods <- readRDS(volmods_file)
  # we assume data is a dataframe with members h, dbh, temp_sum and species
  # where species is an array of enumerations: "pine", "spruce", "birch"
  # and h, dbh and temp_sum are float arrays
  # of equal length (N of trees)
  # returning N-length float array
  prepared_data <- computable_dataframe(tree_data)
  volpred <- vector("numeric", length(tree_data$species))

  volpred[prepared_data$species == "pine"] <- volumes_for_species(prepared_data, "pine", volmods)
  volpred[prepared_data$species == "spruce"] <- volumes_for_species(prepared_data, "spruce", volmods)
  volpred[prepared_data$species == "birch"] <- volumes_for_species(prepared_data, "birch", volmods)
  volpred
}

# result <- compute_tree_volumes(test)