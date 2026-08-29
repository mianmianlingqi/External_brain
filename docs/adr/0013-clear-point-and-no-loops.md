# A Point is Clear only from right latest Verdicts; Tasks hang under a Point; loops are rejected

A Task belongs to exactly one Point, same as a Question. A Point is Clear when it has at least one Question or Task, every one of them has been tried, and the latest Verdict is right. An empty Point is not Clear. A Miss is a Question or Task whose latest Verdict is wrong. A Proposal that would create a before-after loop is rejected at accept time, so the Graph can always sort.
