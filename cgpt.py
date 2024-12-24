# Initial settings
start_price = 1.0030  # Starting price
pip_size = 0.0001    # Size of one pip for EUR/USD
threshold_pips = 15  # Threshold in pips
halfway_threshold = threshold_pips / 2  # Halfway threshold in pips
num_steps = 100      # Number of price changes to simulate
price_changes = [1, -1]  # Simulate alternating up and down movements

# Variables to track thresholds and hedging
current_price = start_price
positive_hedging_triggered = False
negative_hedging_triggered = False

print(f"Start Price: {start_price:.4f}\n")

# Simulate price changes
for step in range(num_steps):
    # Simulate price movement (alternating up and down)
    movement = price_changes[step % 2] * pip_size  # Alternate movement
    current_price += movement

    # Calculate difference and thresholds crossed
    diff = start_price - current_price
    thresholds_crossed = diff / pip_size  # Calculate thresholds in pips

    # Check for 1st threshold (15 pips)
    if abs(thresholds_crossed) >= threshold_pips:
        print(f"Step {step + 1}: Price {current_price:.4f} - Crossed 1st Threshold (15 Pips)!")
        if thresholds_crossed > 0:  # Price moved down
            if not negative_hedging_triggered:
                print(f"Negative Hedging Activated at {current_price:.4f}")
                negative_hedging_triggered = True
        else:  # Price moved up
            if not positive_hedging_triggered:
                print(f"Positive Hedging Activated at {current_price:.4f}")
                positive_hedging_triggered = True

    # Check for 2nd threshold (e.g., 30 pips)
    elif abs(thresholds_crossed) >= threshold_pips * 2:
        print(f"Step {step + 1}: Price {current_price:.4f} - Crossed 2nd Threshold (30 Pips)!")
        if thresholds_crossed > 0:  # Price moved down
            print(f"Negative Hedging Reinforced at {current_price:.4f}")
        else:  # Price moved up
            print(f"Positive Hedging Reinforced at {current_price:.4f}")

    # Check for hedging back to 0.5 threshold
    elif abs(thresholds_crossed) >= halfway_threshold:
        print(f"Step {step + 1}: Price {current_price:.4f} - Crossed Halfway Threshold (7.5 Pips)!")
        if thresholds_crossed > 0:  # Price moving up (negative direction)
            print(f"Negative Hedging Triggered Back at {current_price:.4f}")
        else:  # Price moving down (positive direction)
            print(f"Positive Hedging Triggered Back at {current_price:.4f}")

    # Display current price and direction
    direction = "Up" if diff < 0 else "Down"
    print(f"Step {step + 1}: Price {current_price:.4f}, Diff: {diff:.4f} ({direction})\n")
    