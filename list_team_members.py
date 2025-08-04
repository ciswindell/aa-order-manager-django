#!/usr/bin/env python3
"""
List all team members to help identify the correct team member ID
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, 'src')

from src import config

try:
    import dropbox
except ImportError:
    print("❌ Dropbox SDK not available. Install with: pip install dropbox")
    sys.exit(1)

def list_team_members():
    """List all team members to help identify the correct one."""
    print("👥 Listing Dropbox Business Team Members")
    print("=" * 50)
    
    try:
        # Get team token
        token = config.get_dropbox_access_token()
        if not token:
            print("❌ No DROPBOX_ACCESS_TOKEN found in environment")
            return

        # Create team client
        team_client = dropbox.DropboxTeam(oauth2_access_token=token)
        
        print("📋 Fetching team members...")
        members = team_client.team_members_list()
        
        if not members.members:
            print("❌ No team members found")
            return
            
        print(f"\n🎯 Found {len(members.members)} team members:")
        print("-" * 50)
        
        for i, member in enumerate(members.members, 1):
            profile = member.profile
            print(f"{i}. {profile.name.display_name}")
            print(f"   Email: {profile.email}")
            print(f"   Team Member ID: {profile.team_member_id}")
            # Try to show status if available
            try:
                if hasattr(member, 'status') and hasattr(member.status, '_tag'):
                    print(f"   Status: {member.status._tag}")
            except:
                pass
            print()
            
        print("💡 To use a specific team member:")
        print("1. Add this to your .env file:")
        print("   DROPBOX_TEAM_MEMBER_ID=<your_team_member_id>")
        print("2. Or set it as an environment variable")
        
    except Exception as e:
        print(f"💥 Error listing team members: {str(e)}")

if __name__ == "__main__":
    list_team_members()