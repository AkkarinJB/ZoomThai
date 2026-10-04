FROM rust:slim as builder

# Install dependencies for building WebAssembly
RUN apt-get update && apt-get install -y curl pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*
RUN rustup target add wasm32-unknown-unknown

# Download pre-built trunk to save 4-5 minutes of compilation time
RUN curl -L --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/cargo-bins/cargo-binstall/main/install-from-binstall-release.sh | bash
RUN cargo binstall -y trunk

WORKDIR /app
COPY . .

# Build the Leptos app
RUN trunk build --release

# Serve using a lightweight static file server
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
