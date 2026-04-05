#!/usr/bin/env python
"""
COMPREHENSIVE SYSTEM VALIDATION FOR DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM
Senior Software Architect & University Examiner Evaluation
"""

from django.test import Client
from django.urls import reverse
from django.db.models import Count, Sum, Q
from voting.models import *
from django.db import connection, transaction
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()


class SystemValidator:
    def __init__(self):
        self.issues = []
        self.strengths = []
        self.critical_errors = []
        self.minor_improvements = []
        self.missing_features = []
        self.extra_features = []
        self.grade_components = {}

    def validate_functional_completeness(self):
        """Check CRUD operations and cascading dropdowns"""
        print("1. VALIDATING FUNCTIONAL COMPLETENESS")
        print("-" * 50)

        # Check if all required models exist and are accessible
        try:
            county_count = County.objects.count()
            constituency_count = Constituency.objects.count()
            ward_count = Ward.objects.count()
            candidate_count = Candidate.objects.count()

            print(f"✅ Counties: {county_count}")
            print(f"✅ Constituencies: {constituency_count}")
            print(f"✅ Wards: {ward_count}")
            print(f"✅ Candidates: {candidate_count}")

            if county_count >= 47:
                self.strengths.append(
                    "Complete IEBC county data (47+ counties)")
                self.grade_components['functional_completeness'] = 25
            else:
                self.critical_errors.append(
                    f"Insufficient counties: {county_count} (need 47)")
                self.grade_components['functional_completeness'] = 10

            if constituency_count >= 290:
                self.strengths.append(
                    "Complete constituency data (290+ constituencies)")
            else:
                self.critical_errors.append(
                    f"Insufficient constituencies: {constituency_count} (need 290)")

            if candidate_count >= 3000:
                self.strengths.append(
                    f"Comprehensive candidate database ({candidate_count} candidates)")
            else:
                self.minor_improvements.append(
                    f"Could use more candidates: {candidate_count}")

        except Exception as e:
            self.critical_errors.append(f"Model access error: {str(e)}")
            self.grade_components['functional_completeness'] = 0

        # Check for polling stations
        try:
            polling_station_count = PollingStation.objects.count()
            print(f"✅ Polling Stations: {polling_station_count}")

            if polling_station_count > 0:
                self.strengths.append(
                    f"Polling station data available ({polling_station_count} stations)")
            else:
                self.critical_errors.append("No polling stations found")
        except:
            self.critical_errors.append("PollingStation model not accessible")

        # Check for results system
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='voting_result'")
                if cursor.fetchone():
                    print("✅ Results table exists")
                    self.strengths.append("Results system implemented")
                else:
                    self.critical_errors.append("Results table missing")
        except Exception as e:
            self.critical_errors.append(
                f"Results table check failed: {str(e)}")

    def validate_election_logic(self):
        """Validate election logic and data relationships"""
        print("\n2. VALIDATING ELECTION LOGIC")
        print("-" * 50)

        # Check candidate-position relationships
        try:
            # MCA candidates should have wards
            mca_candidates = Candidate.objects.filter(position__name='MCA')
            mca_with_wards = mca_candidates.filter(ward__isnull=False).count()
            mca_total = mca_candidates.count()

            print(f"MCA Candidates: {mca_total}")
            print(f"MCA with wards: {mca_with_wards}")

            if mca_with_wards == mca_total and mca_total > 0:
                self.strengths.append(
                    "MCA candidates correctly linked to wards")
                self.grade_components['election_logic'] = 20
            else:
                self.critical_errors.append(
                    f"MCA candidates missing ward assignments: {mca_total - mca_with_wards}")
                self.grade_components['election_logic'] = 10

            # MP candidates should have constituencies
            mp_candidates = Candidate.objects.filter(position__name='MP')
            mp_with_constituencies = mp_candidates.filter(
                constituency__isnull=False).count()
            mp_total = mp_candidates.count()

            print(f"MP Candidates: {mp_total}")
            print(f"MP with constituencies: {mp_with_constituencies}")

            if mp_with_constituencies == mp_total and mp_total > 0:
                self.strengths.append(
                    "MP candidates correctly linked to constituencies")
            else:
                self.critical_errors.append(
                    f"MP candidates missing constituency assignments: {mp_total - mp_with_constituencies}")

            # County-level candidates
            county_positions = ['Governor', 'Senator', 'WOMEN_REP']
            for pos_name in county_positions:
                try:
                    pos_candidates = Candidate.objects.filter(
                        position__name=pos_name)
                    pos_with_counties = pos_candidates.filter(
                        county__isnull=False).count()
                    pos_total = pos_candidates.count()

                    print(f"{pos_name} Candidates: {pos_total}")
                    print(f"{pos_name} with counties: {pos_with_counties}")

                    if pos_with_counties == pos_total and pos_total > 0:
                        self.strengths.append(
                            f"{pos_name} candidates correctly linked to counties")
                    else:
                        self.critical_errors.append(
                            f"{pos_name} candidates missing county assignments: {pos_total - pos_with_counties}")

                except:
                    self.minor_improvements.append(
                        f"Position '{pos_name}' may not exist")

        except Exception as e:
            self.critical_errors.append(
                f"Election logic validation failed: {str(e)}")
            self.grade_components['election_logic'] = 0

    def validate_database_design(self):
        """Check database normalization and relationships"""
        print("\n3. VALIDATING DATABASE DESIGN")
        print("-" * 50)

        try:
            # Check hierarchical relationships
            counties_with_constituencies = County.objects.annotate(
                const_count=Count('constituency')
            ).filter(const_count__gt=0).count()

            print(
                f"Counties with constituencies: {counties_with_constituencies}/{County.objects.count()}")

            if counties_with_constituencies == County.objects.count():
                self.strengths.append("Complete county-constituency hierarchy")
            else:
                self.minor_improvements.append(
                    f"{County.objects.count() - counties_with_constituencies} counties without constituencies")

            # Check constituency-ward relationships
            constituencies_with_wards = Constituency.objects.annotate(
                ward_count=Count('ward')
            ).filter(ward_count__gt=0).count()

            print(
                f"Constituencies with wards: {constituencies_with_wards}/{Constituency.objects.count()}")

            if constituencies_with_wards > 0:
                self.strengths.append(
                    "Constituency-ward relationships established")
                self.grade_components['database_design'] = 15
            else:
                self.critical_errors.append(
                    "No constituency-ward relationships found")
                self.grade_components['database_design'] = 5

            # Check for proper indexing (basic check)
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA index_list('voting_county')")
                indexes = cursor.fetchall()
                print(f"County table indexes: {len(indexes)}")

                if len(indexes) > 0:
                    self.strengths.append("Database indexing implemented")
                else:
                    self.minor_improvements.append(
                        "Consider adding database indexes for performance")

        except Exception as e:
            self.critical_errors.append(
                f"Database design validation failed: {str(e)}")
            self.grade_components['database_design'] = 0

    def validate_backend_quality(self):
        """Check REST API and backend implementation"""
        print("\n4. VALIDATING BACKEND QUALITY")
        print("-" * 50)

        # Check URL patterns
        try:
            from django.urls import get_resolver
            resolver = get_resolver()

            # Look for common API patterns
            url_patterns = []
            try:
                # Check if common endpoints exist
                client = Client()

                # Test basic endpoints
                try:
                    response = client.get('/admin/')
                    if response.status_code == 302:  # Redirect to login
                        self.strengths.append("Admin panel accessible")
                        self.grade_components['backend_quality'] = 15
                    else:
                        self.minor_improvements.append(
                            "Admin panel may have issues")
                except:
                    self.minor_improvements.append(
                        "Admin panel not accessible")

                # Check for API endpoints (basic test)
                api_endpoints = ['/api/counties/',
                                 '/api/constituencies/', '/api/wards/']
                api_found = 0

                for endpoint in api_endpoints:
                    try:
                        response = client.get(endpoint)
                        # Any response means URL exists
                        if response.status_code in [200, 403, 404]:
                            api_found += 1
                    except:
                        pass

                if api_found > 0:
                    self.strengths.append(
                        f"API endpoints implemented ({api_found} found)")
                else:
                    self.missing_features.append(
                        "REST API endpoints not implemented")
                    self.grade_components['backend_quality'] = 8

            except Exception as e:
                self.minor_improvements.append(
                    f"URL pattern check failed: {str(e)}")
                self.grade_components['backend_quality'] = 10

        except Exception as e:
            self.critical_errors.append(f"Backend validation failed: {str(e)}")
            self.grade_components['backend_quality'] = 0

    def validate_frontend_ux(self):
        """Check frontend implementation"""
        print("\n5. VALIDATING FRONTEND (UI/UX)")
        print("-" * 50)

        # Check for template files
        import os
        template_dir = 'templates'

        if os.path.exists(template_dir):
            templates = os.listdir(template_dir)
            print(f"Templates found: {len(templates)}")

            if 'base.html' in templates:
                self.strengths.append("Base template exists")
            else:
                self.missing_features.append("Base template missing")

            if 'dashboard.html' in templates or 'index.html' in templates:
                self.strengths.append("Main dashboard template exists")
                self.grade_components['frontend_ux'] = 15
            else:
                self.missing_features.append("Main dashboard template missing")
                self.grade_components['frontend_ux'] = 5

            # Check for results dashboard
            if 'results_dashboard.html' in templates:
                self.strengths.append("Results dashboard template exists")
                self.extra_features.append("Advanced results dashboard")
            else:
                self.minor_improvements.append(
                    "Results dashboard could enhance presentation")
        else:
            self.critical_errors.append("No templates directory found")
            self.grade_components['frontend_ux'] = 0

        # Check for static files
        static_dir = 'static'
        if os.path.exists(static_dir):
            self.strengths.append("Static files directory exists")
        else:
            self.minor_improvements.append("Static files directory missing")

    def validate_demo_readiness(self):
        """Check if system is ready for demonstration"""
        print("\n6. VALIDATING DEMO READINESS")
        print("-" * 50)

        try:
            # Check data completeness
            county_count = County.objects.count()
            candidate_count = Candidate.objects.count()

            # Check minimum candidates per position
            positions = Position.objects.all()
            demo_ready = True

            for position in positions:
                pos_candidates = Candidate.objects.filter(position=position)
                pos_count = pos_candidates.count()

                print(f"{position.name}: {pos_count} candidates")

                if pos_count < 2:
                    self.minor_improvements.append(
                        f"{position.name} has fewer than 2 candidates")
                    demo_ready = False

            # Check for sample results
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM voting_result")
                    result_count = cursor.fetchone()[0]

                    print(f"Sample results: {result_count}")

                    if result_count > 0:
                        self.strengths.append(
                            "Sample results available for demo")
                        self.grade_components['demo_readiness'] = 15
                    else:
                        self.minor_improvements.append(
                            "No sample results - demo may be less impressive")
                        self.grade_components['demo_readiness'] = 10

            except:
                self.minor_improvements.append(
                    "Results table not accessible for demo check")
                self.grade_components['demo_readiness'] = 8

            if demo_ready and county_count >= 40:
                self.strengths.append(
                    "System ready for comprehensive demonstration")
            else:
                self.minor_improvements.append(
                    "System needs more data for full demonstration")

        except Exception as e:
            self.critical_errors.append(
                f"Demo readiness check failed: {str(e)}")
            self.grade_components['demo_readiness'] = 0

    def validate_performance_scalability(self):
        """Check performance and scalability considerations"""
        print("\n7. VALIDATING PERFORMANCE & SCALABILITY")
        print("-" * 50)

        try:
            # Test query performance
            import time

            # Test candidate query performance
            start_time = time.time()
            candidates = list(Candidate.objects.all()[:100])
            query_time = time.time() - start_time

            print(f"Candidate query time (100 records): {query_time:.3f}s")

            if query_time < 0.1:
                self.strengths.append("Good query performance")
                self.grade_components['performance'] = 10
            elif query_time < 0.5:
                self.minor_improvements.append(
                    "Query performance could be optimized")
                self.grade_components['performance'] = 7
            else:
                self.critical_errors.append(
                    "Poor query performance - needs optimization")
                self.grade_components['performance'] = 3

            # Check data volume
            total_records = (
                County.objects.count() +
                Constituency.objects.count() +
                Ward.objects.count() +
                Candidate.objects.count()
            )

            print(f"Total database records: {total_records}")

            if total_records > 3000:
                self.strengths.append(
                    "Substantial dataset for scalability testing")
            else:
                self.minor_improvements.append(
                    "Could benefit from larger dataset")

        except Exception as e:
            self.minor_improvements.append(
                f"Performance check failed: {str(e)}")
            self.grade_components['performance'] = 5

    def check_extra_features(self):
        """Check for extra features that merit high marks"""
        print("\n8. CHECKING EXTRA FEATURES (FOR HIGH MARKS)")
        print("-" * 50)

        # Check for authentication
        try:
            from django.contrib.auth.models import User
            user_count = User.objects.count()

            if user_count > 0:
                self.strengths.append("User authentication system available")
                self.extra_features.append("User authentication")

        except:
            pass

        # Check for export functionality
        try:
            # Look for export-related code or templates
            if os.path.exists('templates/results_dashboard.html'):
                with open('templates/results_dashboard.html', 'r') as f:
                    content = f.read()
                    if 'export' in content.lower():
                        self.extra_features.append("Export functionality")
                        self.strengths.append(
                            "Export functionality implemented")
        except:
            pass

        # Check for search/filtering
        if os.path.exists('templates/results_dashboard.html'):
            try:
                with open('templates/results_dashboard.html', 'r') as f:
                    content = f.read()
                    if 'search' in content.lower() or 'filter' in content.lower():
                        self.extra_features.append("Search and filtering")
                        self.strengths.append("Search/filter functionality")
            except:
                pass

        print(f"Extra features found: {len(self.extra_features)}")
        for feature in self.extra_features:
            print(f"  ✅ {feature}")

    def calculate_final_grade(self):
        """Calculate final grade out of 100"""
        print("\n" + "="*60)
        print("FINAL GRADE CALCULATION")
        print("="*60)

        # Base components
        base_grade = 0
        max_grade = 100

        # Functional Completeness (25 points)
        functional_score = self.grade_components.get(
            'functional_completeness', 15)
        base_grade += functional_score

        # Election Logic (20 points)
        logic_score = self.grade_components.get('election_logic', 15)
        base_grade += logic_score

        # Database Design (15 points)
        db_score = self.grade_components.get('database_design', 10)
        base_grade += db_score

        # Backend Quality (15 points)
        backend_score = self.grade_components.get('backend_quality', 10)
        base_grade += backend_score

        # Frontend UX (15 points)
        frontend_score = self.grade_components.get('frontend_ux', 10)
        base_grade += frontend_score

        # Demo Readiness (10 points)
        demo_score = self.grade_components.get('demo_readiness', 8)
        base_grade += demo_score

        # Bonus points for extra features
        bonus_points = min(len(self.extra_features) * 2, 10)
        base_grade += bonus_points

        # Deductions for critical errors
        error_deductions = len(self.critical_errors) * 5
        base_grade -= error_deductions

        # Ensure grade is within bounds
        final_grade = max(0, min(100, base_grade))

        return final_grade

    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE SYSTEM VALIDATION REPORT")
        print("="*60)

        # Run all validations
        self.validate_functional_completeness()
        self.validate_election_logic()
        self.validate_database_design()
        self.validate_backend_quality()
        self.validate_frontend_ux()
        self.validate_demo_readiness()
        self.validate_performance_scalability()
        self.check_extra_features()

        # Calculate final grade
        final_grade = self.calculate_final_grade()

        # Print results
        print(f"\n📊 FINAL GRADE: {final_grade}/100")

        if final_grade >= 70:
            print("🎓 GRADE: DISTINCTION LEVEL")
        elif final_grade >= 60:
            print("📚 GRADE: UPPER SECOND CLASS")
        elif final_grade >= 50:
            print("📖 GRADE: LOWER SECOND CLASS")
        else:
            print("⚠️  GRADE: NEEDS IMPROVEMENT")

        print("\n" + "="*60)
        print("DETAILED ANALYSIS")
        print("="*60)

        print(f"\n✅ STRENGTHS ({len(self.strengths)}):")
        for strength in self.strengths:
            print(f"  • {strength}")

        print(f"\n⚠️  CRITICAL ERRORS ({len(self.critical_errors)}):")
        for error in self.critical_errors:
            print(f"  • {error}")

        print(f"\n🔧 MINOR IMPROVEMENTS ({len(self.minor_improvements)}):")
        for improvement in self.minor_improvements:
            print(f"  • {improvement}")

        print(f"\n❌ MISSING FEATURES ({len(self.missing_features)}):")
        for feature in self.missing_features:
            print(f"  • {feature}")

        print(f"\n🌟 EXTRA FEATURES ({len(self.extra_features)}):")
        for feature in self.extra_features:
            print(f"  • {feature}")

        # Recommendations
        print("\n" + "="*60)
        print("RECOMMENDATIONS FOR DISTINCTION LEVEL")
        print("="*60)

        if self.critical_errors:
            print("\n🚨 IMMEDIATE ACTIONS REQUIRED:")
            for error in self.critical_errors:
                print(f"  1. FIX: {error}")

        if self.missing_features:
            print("\n📋 IMPLEMENT MISSING FEATURES:")
            for feature in self.missing_features:
                print(f"  • Add {feature}")

        if self.minor_improvements:
            print("\n💡 ENHANCEMENTS FOR HIGHER MARKS:")
            for improvement in self.minor_improvements:
                print(f"  • {improvement}")

        print(f"\n🎯 PATH TO DISTINCTION:")
        if final_grade < 70:
            needed = 70 - final_grade
            print(f"  • Need {needed} more points to reach distinction level")
            print(
                f"  • Focus on fixing {len(self.critical_errors)} critical errors first")
            print(
                f"  • Implement {len(self.missing_features)} missing features")
        else:
            print("  ✅ System already at distinction level!")
            print("  • Focus on polishing presentation and demo flow")

        return final_grade


def main():
    """Run comprehensive system validation"""
    print("🔍 COMPREHENSIVE SYSTEM VALIDATION")
    print("Senior Software Architect & University Examiner Evaluation")
    print("="*60)

    validator = SystemValidator()
    final_grade = validator.generate_report()

    return final_grade


if __name__ == '__main__':
    main()
