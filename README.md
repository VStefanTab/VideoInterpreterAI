# Real-Time Video Interpreters
This project explores two simple approaches to video interpretation using modern AI models. The goal is to compare how different tools handle the balance between speed and interpretive depth when analyzing live video streams and also recorded videos.

## Overview
1. **BLIP Interpreter**<br>
This version focuses on real-time performance. It uses BLIP to generate short captions. The output is immediate and simple, offering basic scene descriptions.

2. **LLamaCPP Interpreter (Jetson Containers)**<br>
This version aims for more detailed summaries. It runs LLamaCPP in a containerized setup on NVIDIA Jetson hardware. It processes video slower, but it can generate richer and more contextual descriptions by working with more information at once.

## How to use?
Please check each interpreter's README for instructions.
