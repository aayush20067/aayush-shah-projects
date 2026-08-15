1. loaded 6 races (fastf1) - done
2. cleaned data (accurate laps, no pits, no outliers) - done
3. created features (LapInStint, StintID, RaceTime, GapAhead/Behind) - done
4. built degradation signal (DeltaT, SmoothedDeltaT) - done
5. labeled data (Clean vs Noisy using gaps) - done
6. added MLP features (lag, diff, rolling std, lap position) - done
7. trained MLP → CleanProb - done
8. evaluated MLP (AUC) - done
9. applied CleanProb to full dataset - done
10. built regression dataset (LapInStint, Lap², Compound + weights) - done
11. trained regression (Ridge → Gradient Boosting) - done
12. plotted + smoothed degradation curves - done
13. test performace of ridge and gradient boosting on a out of sample set after applying our initial MLP done
15. woh nayi cheez (with reace encoding)
14. model new metrics to decide whether a lap is clean or no based on telemetry data in the dataset and compute them and store them
15. create new labels to check if a lap is clean for degradation modelling
16. train the new MLP on these labels and features 
17. Evaluate the performance of this new MLP
18. after generating cleanprob2 build a new regression dataset
19. and train ridge regression and gradient boosting on the dataset
20. train a random forest on both MLP
21. train a basic mlp on both models of the MLP
22. test performance metrics in all cases (8 performance comparisons)



    After testing on an unseen race, the model showed very poor generalization (strongly negative R²). This highlighted that a global model based only on stint position and compound is insufficient. The key insight was that tyre degradation is strongly track-dependent, and the model was missing any notion of track context.
To address this, the regression model was extended by adding Race as a categorical feature and retrained on a larger dataset (~20–25 races). This led to a significant improvement in performance, showing that race encoding helps capture track-specific degradation behaviour and improves generalization within similar data.

Final insight
Even after adding Race, performance on a different year (e.g., 2024 → 2023) remained weak. This shows that race encoding is only a proxy and does not capture true track physics, and also that seasonal differences introduce distribution shift (car performance, setups, conditions).
The final conclusion is that while CleanProb improves noise handling and local fit, true generalization requires physically meaningful track-level features, not just categorical race labels.