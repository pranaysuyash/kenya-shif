#!/usr/bin/env python3
"""
Test the integrated simple tabula approach in the main analyzer
Focus on tabula-only extraction without AI processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generalized_medical_analyzer import GeneralizedMedicalAnalyzer

def test_simple_tabula_integration():
    """Test just the simple tabula extraction functionality"""
    
    print("🧪 TESTING SIMPLE TABULA INTEGRATION")
    print("=" * 50)
    
    # Initialize analyzer without API key to skip AI processing
    print("   🔧 Initializing analyzer (no AI, tabula only)...")
    analyzer = GeneralizedMedicalAnalyzer(api_key=None)
    
    # Test the simple tabula extraction methods directly
    print("   📊 Testing simple tabula tariff extraction...")
    tariffs = analyzer._extract_tariffs_tabula()
    print(f"   ✅ Extracted {len(tariffs)} tariffs")
    
    if tariffs:
        # Show sample tariffs
        print("\n📋 SAMPLE TARIFFS:")
        for i, tariff in enumerate(tariffs[:5]):
            specialty = tariff.get('specialty', 'Unknown')
            service = tariff.get('service_name', 'Unknown')
            price = tariff.get('price_kes', 0)
            print(f"   {i+1}. {specialty} | {service[:50]}... | KES {price:,.0f}")
    
    print("   📊 Testing simple tabula service extraction...")  
    services = analyzer._extract_services_simple_tabula()
    print(f"   ✅ Extracted {len(services)} services")
    
    if services:
        # Show sample services
        print("\n📋 SAMPLE SERVICES:")
        for i, service in enumerate(services[:5]):
            specialty = service.get('specialty', 'Unknown')
            name = service.get('service_name', 'Unknown')
            tariff = service.get('tariff_amount', 0)
            tariff_text = f"KES {tariff:,.0f}" if tariff else "No tariff"
            print(f"   {i+1}. {specialty} | {name[:50]}... | {tariff_text}")
    
    # Test specialty analysis
    if tariffs:
        print("\n🏥 SPECIALTY ANALYSIS:")
        specialties = {}
        for tariff in tariffs:
            specialty = tariff.get('specialty', 'Unknown')
            if specialty not in specialties:
                specialties[specialty] = {'count': 0, 'total_value': 0}
            specialties[specialty]['count'] += 1
            specialties[specialty]['total_value'] += tariff.get('price_kes', 0)
        
        # Sort by count
        sorted_specialties = sorted(specialties.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for specialty, data in sorted_specialties[:10]:
            avg_tariff = data['total_value'] / data['count'] if data['count'] > 0 else 0
            print(f"   • {specialty}: {data['count']} procedures (avg: KES {avg_tariff:,.0f})")
    
    print(f"\n✅ INTEGRATION TEST COMPLETED")
    print(f"   Total tariffs: {len(tariffs)}")
    print(f"   Total services: {len(services)}")
    print(f"   Success: Simple tabula integration working!")
    
    return tariffs, services

if __name__ == "__main__":
    tariffs, services = test_simple_tabula_integration()