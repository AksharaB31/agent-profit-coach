class ConvenienceEngine:
    """Scores flight duration and stops."""
    
    def calculate_score(self, duration: int, stops: int, min_duration: int, max_duration: int) -> float:
        # Stop penalty: direct = 100, 1 stop = 70, 2+ stops = 40
        stop_score = 100.0 if stops == 0 else (70.0 if stops == 1 else 40.0)
        
        # Duration score using min-max normalization (shorter is better)
        if max_duration == min_duration:
            duration_score = 100.0
        else:
            duration_score = 100.0 * (1.0 - ((duration - min_duration) / (max_duration - min_duration)))
            
        return (stop_score * 0.6) + (duration_score * 0.4)
