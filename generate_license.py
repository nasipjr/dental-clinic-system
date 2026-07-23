#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.license_helper import generate_license_key, verify_license_key

def main():
    print("=================================================================")
    print(" Dental Clinic MS - Developer License Key Generator ")
    print("=================================================================")

    days = 30
    license_type = "trial"

    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        if arg in ["lifetime", "life"]:
            days = 36500
            license_type = "lifetime"
        else:
            try:
                days = int(arg)
                if days >= 365:
                    license_type = "annual"
                else:
                    license_type = "trial"
            except ValueError:
                print(f"X Invalid argument '{sys.argv[1]}'. Pass number of days or 'lifetime'.")
                sys.exit(1)

    key = generate_license_key(days=days, license_type=license_type)
    is_valid, info = verify_license_key(key)

    print(f"\nLicense Key:       {key}")
    print(f"License Type:      {license_type.upper()}")
    print(f"Validity Period:   {days} Days")
    if is_valid and isinstance(info, dict):
        print(f"Expiration Date:   {info['expires_at'].strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nCopy & paste this key into the activation screen or .env file.")
    print("=================================================================")

if __name__ == "__main__":
    main()
