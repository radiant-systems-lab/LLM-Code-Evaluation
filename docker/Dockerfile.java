FROM maven:3.9-eclipse-temurin-17
WORKDIR /work
# No pre-installed packages - clean Maven cache for each project
CMD ["bash"]
