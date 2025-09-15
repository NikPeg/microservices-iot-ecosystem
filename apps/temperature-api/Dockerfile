# Minimal Dockerfile using scratch base image
FROM scratch

# Copy the pre-built binary
COPY temperature-api /temperature-api

# Expose port 8081
EXPOSE 8081

# Set environment variables
ENV PORT=8081
ENV GIN_MODE=release

# Run the application
CMD ["/temperature-api"]