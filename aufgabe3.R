library(tuneR)
library(seewave)
library(fields)
library(viridis)

print_memory_usage <- function(stage) {
  rss <- memory.size(max = TRUE)
  vms <- sum(vapply(ls(envir = globalenv()), function(x) { object.size(get(x, envir = globalenv())) }, numeric(1)))
  cat(stage, ": RSS =", rss / (1024 ^ 2), "MB, VMS =", vms / (1024 ^ 2), "MB\n")
}

analyze_wav <- function(file_path, block_size, overlap) {
  print_memory_usage("Start")
  
  # Read WAV file
  wav <- readWave(file_path)
  sample_rate <- wav@samp.rate
  data <- as.numeric(wav@left)
  cat("Sample Rate:", sample_rate, "Hz\n")
  print_memory_usage("After reading WAV file")
  
  # Compute Spectrogram
  spec <- spectro(data, f = sample_rate, wl = block_size, ovlp = overlap / block_size * 100, plot = FALSE)
  Sxx <- spec$amp
  f <- spec$freq
  t <- spec$time
  print_memory_usage("After computing spectrogram")
  
  # Handle NaN values
  if(any(is.na(Sxx))) {
    cat("NaN values found in spectrogram data. Replacing NaNs with minimum non-NaN value.\n")
    min_non_nan <- min(Sxx, na.rm = TRUE)
    Sxx[is.na(Sxx)] <- min_non_nan
  }
  
  # Check for NaN values again and replace with a small value if any still exist
  Sxx[is.na(Sxx)] <- min(Sxx[!is.na(Sxx)], na.rm = TRUE)
  
  # Plot Spectrogram
  image.plot(t, f, 10 * log10(Sxx), zlim = c(min(10 * log10(Sxx), na.rm = TRUE), max(10 * log10(Sxx), na.rm = TRUE)),
             xlab = "Time [sec]", ylab = "Frequency [Hz]", main = paste("Spectrogram of the WAV file with Block size =", block_size),
             col = grey.colors(100), breaks = 100)
  color.legend(legend = "Intensity [dB]", at = seq(min(10 * log10(Sxx), na.rm = TRUE), max(10 * log10(Sxx), na.rm = TRUE), length.out = 5))
  
  print_memory_usage("After plotting")
}

# Path to WAV file and block size
file_path <- "C:/Users/mohad/PycharmProjects/fourier/nicht_zu_laut_abspielen.wav"
block_size <- 1024  # Block size
overlap <- block_size / 2  # 50% overlap

analyze_wav(file_path, block_size, overlap)
