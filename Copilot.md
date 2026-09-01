I prepared both requested solutions in English. The analysis respects the repeated-measures structure by avoiding a Kruskal-Wallis test on all 357 dependent observations as if they were independent.



Files

Download the complete Python script

Download the explanatory Jupyter notebook

Main methodological choices



The implementations provide:



Kruskal-Wallis omnibus tests for both TTU and DOU

Analyses:

across the complete study using one median per participant

separately for each task

separately for every structural task aspect such as COMP, COND, LOOK, CELL, and RANGE

Kruskal-Wallis epsilon-squared as the omnibus effect size

Pairwise Mann-Whitney U tests for all three group comparisons

Signed rank-biserial correlations as pairwise effect sizes

Holm correction:

across task-level or aspect-level omnibus tests

across the three pairwise comparisons within each analysis

Compact letter displays

Medians, quartiles, means, standard deviations, and sample sizes

CSV output files containing all results



For the overall and structural-aspect analyses, repeated observations are first aggregated to one median per participant. This prevents pseudoreplication. For a single task, every participant already supplies only one value, so the ordinary between-subject Kruskal-Wallis analysis is appropriate.



Preliminary result from the supplied data



The data contain:



357 observations

21 participants

17 tasks

7 participants per construction group

247 DOU values equal to 1.0, corresponding to 69.2%



After Holm correction across the 17 task-level tests, the script identified one significant omnibus result:



Task 15, DOU:

&#x20;H(2)=13.604H(2)=13.604, raw p=0.00111p=0.00111, Holm-adjusted p=0.01890p=0.01890, epsilon-squared =0.645=0.645



No other per-task omnibus test remained significant after the family-wise Holm correction in this implementation. The generated output tables provide the corresponding pairwise comparisons, rank-biserial effect sizes, group medians, and compact letters.



Running the Python script



Place the script and study\_data.csv in the same directory and run:



python study\_statistics.py





Alternatively, specify paths explicitly:



python study\_statistics.py \\

&#x20;   --input study\_data.csv \\

&#x20;   --output study\_results





The script creates:



study\_results/

├── data\_audit.csv

├── descriptives\_and\_cld.csv

├── omnibus\_tests.csv

└── pairwise\_tests.csv



Output interpretation



omnibus\_tests.csv



Kruskal-Wallis H statistic

raw p-value

family-wise Holm-adjusted p-value

epsilon-squared

significance indicators



pairwise\_tests.csv



Mann-Whitney U

raw and Holm-adjusted p-values

signed rank-biserial correlation

difference between group medians



descriptives\_and\_cld.csv



sample size

median

first and third quartiles

mean and standard deviation

compact-letter display



Groups that share a letter are not significantly different according to the Holm-adjusted pairwise tests. Groups with no letter in common are significantly different. Sharing a letter should not be interpreted as proof of equivalence.



Important statistical qualification



A “Kruskal-Wallis test with within=task and between=group” does not exist in the ordinary Kruskal-Wallis framework. Kruskal-Wallis assumes independent observations and cannot directly model a within-subject factor.



The supplied implementation therefore answers three defensible questions:



Overall: Do the groups differ in participants’ typical performance across tasks?

Per task: Do groups differ for this particular task?

Per structural aspect: Do groups differ in participants’ typical performance across tasks carrying this aspect?



A formal test of the group × task interaction would require a mixed-effects, generalized estimating-equation, cumulative-link mixed, or specialized rank-based repeated-measures model. With only seven participants per group and a very strong DOU ceiling effect, such models may be unstable and should be treated as exploratory.

