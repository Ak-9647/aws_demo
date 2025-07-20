#!/usr/bin/env python3
"""
AWS Resource Manager
Advanced resource cleanup and cost management tool
"""

import boto3
import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse

class AWSResourceManager:
    def __init__(self, region: str = "us-west-2"):
        self.region = region
        self.ecs = boto3.client('ecs', region_name=region)
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.ec2 = boto3.client('ec2', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer is only in us-east-1
        
        self.cluster_name = "production-analytics-agent-cluster"
        self.service_name = "production-analytics-agent-gui-service"
    
    def get_current_costs(self) -> Dict:
        """Get current AWS costs for the last 7 days"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            response = self.ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            costs = {}
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['BlendedCost']['Amount'])
                    if service not in costs:
                        costs[service] = 0
                    costs[service] += cost
            
            return costs
        except Exception as e:
            print(f"⚠️  Could not retrieve cost data: {e}")
            return {}
    
    def get_ecs_status(self) -> Dict:
        """Get ECS service status"""
        try:
            response = self.ecs.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            
            if response['services']:
                service = response['services'][0]
                return {
                    'status': service['status'],
                    'running_count': service['runningCount'],
                    'desired_count': service['desiredCount'],
                    'task_definition': service['taskDefinition']
                }
            else:
                return {'status': 'NOT_FOUND'}
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def get_load_balancers(self) -> List[Dict]:
        """Get load balancer information"""
        try:
            response = self.elbv2.describe_load_balancers()
            analytics_lbs = []
            
            for lb in response['LoadBalancers']:
                if 'analytics' in lb['LoadBalancerName'].lower():
                    analytics_lbs.append({
                        'name': lb['LoadBalancerName'],
                        'arn': lb['LoadBalancerArn'],
                        'state': lb['State']['Code'],
                        'type': lb['Type'],
                        'dns_name': lb['DNSName']
                    })
            
            return analytics_lbs
        except Exception as e:
            print(f"⚠️  Error getting load balancers: {e}")
            return []
    
    def get_nat_gateways(self) -> List[Dict]:
        """Get NAT gateway information"""
        try:
            response = self.ec2.describe_nat_gateways()
            active_nats = []
            
            for nat in response['NatGateways']:
                if nat['State'] == 'available':
                    active_nats.append({
                        'id': nat['NatGatewayId'],
                        'state': nat['State'],
                        'subnet_id': nat['SubnetId']
                    })
            
            return active_nats
        except Exception as e:
            print(f"⚠️  Error getting NAT gateways: {e}")
            return []
    
    def get_elastic_ips(self) -> List[Dict]:
        """Get Elastic IP information"""
        try:
            response = self.ec2.describe_addresses()
            return [
                {
                    'ip': addr['PublicIp'],
                    'allocation_id': addr['AllocationId'],
                    'associated': 'AssociationId' in addr
                }
                for addr in response['Addresses']
            ]
        except Exception as e:
            print(f"⚠️  Error getting Elastic IPs: {e}")
            return []
    
    def scale_ecs_service(self, desired_count: int) -> bool:
        """Scale ECS service to specified count"""
        try:
            self.ecs.update_service(
                cluster=self.cluster_name,
                service=self.service_name,
                desiredCount=desired_count
            )
            print(f"✅ ECS service scaled to {desired_count}")
            return True
        except Exception as e:
            print(f"❌ Error scaling ECS service: {e}")
            return False
    
    def run_terraform_destroy(self, targets: List[str] = None) -> bool:
        """Run terraform destroy with optional targets"""
        try:
            cmd = ["terraform", "destroy"]
            
            if targets:
                for target in targets:
                    cmd.extend(["-target", target])
            
            cmd.append("-auto-approve")
            
            result = subprocess.run(
                cmd,
                cwd="infrastructure",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Terraform destroy completed successfully")
                return True
            else:
                print(f"❌ Terraform destroy failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running terraform: {e}")
            return False
    
    def run_terraform_apply(self) -> bool:
        """Run terraform apply to restore resources"""
        try:
            result = subprocess.run(
                ["terraform", "apply", "-auto-approve"],
                cwd="infrastructure",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Terraform apply completed successfully")
                return True
            else:
                print(f"❌ Terraform apply failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running terraform: {e}")
            return False
    
    def show_resource_summary(self):
        """Display comprehensive resource summary"""
        print("📊 AWS Resource Summary")
        print("=" * 50)
        
        # ECS Status
        ecs_status = self.get_ecs_status()
        print(f"🐳 ECS Service: {ecs_status.get('status', 'UNKNOWN')}")
        if ecs_status.get('status') == 'ACTIVE':
            print(f"   Running: {ecs_status['running_count']}/{ecs_status['desired_count']}")
        
        # Load Balancers
        lbs = self.get_load_balancers()
        print(f"⚖️  Load Balancers: {len(lbs)} found")
        for lb in lbs:
            print(f"   {lb['name']}: {lb['state']}")
        
        # NAT Gateways
        nats = self.get_nat_gateways()
        print(f"🌐 NAT Gateways: {len(nats)} active")
        
        # Elastic IPs
        eips = self.get_elastic_ips()
        print(f"📍 Elastic IPs: {len(eips)} allocated")
        
        # Cost Information
        costs = self.get_current_costs()
        if costs:
            print("\n💰 Recent Costs (Last 7 days):")
            total_cost = 0
            for service, cost in sorted(costs.items(), key=lambda x: x[1], reverse=True):
                if cost > 0.01:  # Only show costs > $0.01
                    print(f"   {service}: ${cost:.2f}")
                    total_cost += cost
            print(f"   TOTAL: ${total_cost:.2f}")
        
        print("\n💡 Estimated Monthly Savings:")
        print("   Scale down ECS: ~$18/month")
        print("   Remove expensive resources: ~$68/month")
        print("   Destroy all: ~$95/month")
    
    def cleanup_mode_1(self):
        """Mode 1: Scale down ECS service only"""
        print("📉 Mode 1: Scaling down ECS service...")
        if self.scale_ecs_service(0):
            print("💰 Estimated monthly savings: ~$18")
            print("📝 To restart: python3 scripts/resource_manager.py --restart-ecs")
    
    def cleanup_mode_2(self):
        """Mode 2: Remove expensive resources"""
        print("💰 Mode 2: Removing expensive resources...")
        
        targets = [
            "aws_nat_gateway.main",
            "aws_eip.nat",
            "aws_lb.gui",
            "aws_lb_listener.gui",
            "aws_lb_target_group.gui",
            "aws_security_group.alb",
            "aws_ecs_service.gui"
        ]
        
        if self.run_terraform_destroy(targets):
            print("💰 Estimated monthly savings: ~$68")
            print("📝 To restart: python3 scripts/resource_manager.py --restart-all")
    
    def cleanup_mode_3(self):
        """Mode 3: Destroy all infrastructure"""
        print("🔥 Mode 3: DESTROYING ALL INFRASTRUCTURE...")
        print("⚠️  This will remove everything except S3 data!")
        
        confirm = input("Are you sure? Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("❌ Cancelled")
            return
        
        if self.run_terraform_destroy():
            print("💰 Estimated monthly savings: ~$95")
            print("📝 To restart: python3 scripts/resource_manager.py --restart-all")
    
    def restart_ecs(self):
        """Restart ECS service"""
        print("🚀 Restarting ECS service...")
        self.scale_ecs_service(1)
    
    def restart_all(self):
        """Restart all services"""
        print("🚀 Restarting all services...")
        self.run_terraform_apply()

def main():
    parser = argparse.ArgumentParser(description='AWS Resource Manager')
    parser.add_argument('--status', action='store_true', help='Show resource status')
    parser.add_argument('--cleanup-1', action='store_true', help='Scale down ECS only')
    parser.add_argument('--cleanup-2', action='store_true', help='Remove expensive resources')
    parser.add_argument('--cleanup-3', action='store_true', help='Destroy all infrastructure')
    parser.add_argument('--restart-ecs', action='store_true', help='Restart ECS service')
    parser.add_argument('--restart-all', action='store_true', help='Restart all services')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    manager = AWSResourceManager()
    
    if args.status:
        manager.show_resource_summary()
    elif args.cleanup_1:
        manager.cleanup_mode_1()
    elif args.cleanup_2:
        manager.cleanup_mode_2()
    elif args.cleanup_3:
        manager.cleanup_mode_3()
    elif args.restart_ecs:
        manager.restart_ecs()
    elif args.restart_all:
        manager.restart_all()
    elif args.interactive or len(sys.argv) == 1:
        # Interactive mode
        while True:
            print("\n🧹 AWS Resource Manager")
            print("=" * 30)
            print("1) Show resource status")
            print("2) Scale down ECS only (save $18/month)")
            print("3) Remove expensive resources (save $68/month)")
            print("4) DESTROY all infrastructure (save $95/month)")
            print("5) Restart ECS service")
            print("6) Restart all services")
            print("7) Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                manager.show_resource_summary()
            elif choice == '2':
                manager.cleanup_mode_1()
            elif choice == '3':
                manager.cleanup_mode_2()
            elif choice == '4':
                manager.cleanup_mode_3()
            elif choice == '5':
                manager.restart_ecs()
            elif choice == '6':
                manager.restart_all()
            elif choice == '7':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")
            
            input("\nPress Enter to continue...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()