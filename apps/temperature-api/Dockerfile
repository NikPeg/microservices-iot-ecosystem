# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o temperature-api .

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates wget
WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/temperature-api .

# Expose port
EXPOSE 8083

# Set environment variables
ENV PORT=8083
ENV GIN_MODE=release

# Run the application
CMD ["./temperature-api"]
