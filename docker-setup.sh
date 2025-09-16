#!/bin/bash

# K12 LMS Docker Setup Script
# This script sets up and runs the K12 LMS using Docker Compose

set -e

echo "🐳 K12 LMS Docker Setup"
echo "========================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to check if services are running
check_services() {
    echo "🔍 Checking service health..."
    
    # Check API health
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        echo "✅ API service is healthy"
    else
        echo "❌ API service is not responding"
        return 1
    fi
    
    # Check Web health
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Web service is healthy"
    else
        echo "❌ Web service is not responding"
        return 1
    fi
    
    return 0
}

# Function to seed the database
seed_database() {
    echo "🌱 Seeding database..."
    
    # Wait for API to be ready
    echo "⏳ Waiting for API to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/api/health &> /dev/null; then
            echo "✅ API is ready"
            break
        fi
        echo "⏳ Waiting for API... ($i/30)"
        sleep 2
    done
    
    # Run database seeding
    docker compose exec api python -m db.seed
    echo "✅ Database seeded successfully"
}

# Main setup function
setup() {
    echo "🚀 Starting K12 LMS with Docker Compose..."
    
    # Build and start services
    docker compose up --build -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check if services are healthy
    if check_services; then
        echo ""
        echo "🎉 K12 LMS is running successfully!"
        echo ""
        echo "📋 Access Information:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend API: http://localhost:8000"
        echo "  API Documentation: http://localhost:8000/docs"
        echo ""
        echo "👤 Demo Credentials:"
        echo "  Teacher: teacher@example.com / pass"
        echo "  Student: student@example.com / pass"
        echo "  Student2: student2@example.com / pass"
        echo "  Student3: student3@example.com / pass"
        echo ""
        
        # Ask if user wants to seed database
        read -p "🌱 Would you like to seed the database with demo data? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            seed_database
        fi
        
        echo ""
        echo "🎯 Next Steps:"
        echo "  1. Open http://localhost:3000 in your browser"
        echo "  2. Log in with demo credentials"
        echo "  3. Explore the features!"
        echo ""
        echo "🛑 To stop the services, run: docker compose down"
        
    else
        echo "❌ Services failed to start properly. Check the logs:"
        echo "  docker compose logs"
        exit 1
    fi
}

# Function to stop services
stop() {
    echo "🛑 Stopping K12 LMS services..."
    docker compose down
    echo "✅ Services stopped"
}

# Function to show logs
logs() {
    echo "📋 Showing service logs..."
    docker compose logs -f
}

# Function to show status
status() {
    echo "📊 Service Status:"
    docker compose ps
    echo ""
    if check_services; then
        echo "✅ All services are healthy"
    else
        echo "❌ Some services are not responding"
    fi
}

# Function to clean up
clean() {
    echo "🧹 Cleaning up Docker resources..."
    docker compose down -v
    docker system prune -f
    echo "✅ Cleanup complete"
}

# Main script logic
case "${1:-setup}" in
    "setup"|"start")
        setup
        ;;
    "stop")
        stop
        ;;
    "restart")
        stop
        setup
        ;;
    "logs")
        logs
        ;;
    "status")
        status
        ;;
    "seed")
        seed_database
        ;;
    "clean")
        clean
        ;;
    "help"|"-h"|"--help")
        echo "K12 LMS Docker Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup, start  - Build and start all services (default)"
        echo "  stop          - Stop all services"
        echo "  restart       - Restart all services"
        echo "  logs          - Show service logs"
        echo "  status        - Show service status"
        echo "  seed          - Seed the database with demo data"
        echo "  clean         - Stop services and clean up resources"
        echo "  help          - Show this help message"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
