FROM continuumio/miniconda3:latest
# Set timezone and suppress interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

WORKDIR /app

# Install system dependencies for OpenCASCADE rendering + X11 client libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libglu1-mesa \
    mesa-utils \
    libegl1-mesa \
    libgbm1 \
    libosmesa6 \
    libosmesa6-dev \
    libx11-6 \
    libgtk-3-0 \
    libxrender1 \
    libxext6 \
    libgdk-pixbuf2.0-0 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxinerama1 \
    libxcb1 \
    x11-apps \
    x11-utils \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Copy environment first to leverage Docker cache
COPY environment.yml .

# Create Conda environment using libmamba solver
RUN conda install -n base conda-libmamba-solver && \
    conda config --set solver libmamba && \
    conda env create -f environment.yml && \
    conda clean -afy

# Set environment path
ENV PATH /opt/conda/envs/brep_manipulation/bin:$PATH

# Copy source code
COPY . .

# Make startup script executable
RUN chmod +x entrypoint.sh

# DISPLAY will be set via docker-compose environment
ENV DISPLAY=:1

# Force software OpenGL rendering for container compatibility
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MESA_GL_VERSION_OVERRIDE=3.3
ENV GALLIUM_DRIVER=llvmpipe

# Use conda + entrypoint script
ENTRYPOINT ["./entrypoint.sh"]