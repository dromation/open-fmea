from __future__ import annotations

from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from django.db import transaction

from fmea_domain import ActionStatus, CauseInfluenceStatus, FMEALifecycle
from fmea_evaluation import (
    ACTION_PRIORITY_POC_METHOD,
    AIAG_VDA_AP_METHOD,
    AIAG_VDA_MSR_METHOD,
    CLASSIC_RPN_METHOD,
)

from fmea_app import models
from fmea_app.management.commands.seed_cause_category_scheme import (
    DEFAULT_CATEGORIES,
    DEFAULT_SCHEME_STABLE_ID,
)
from fmea_app.services import evaluate_failure_mode


DEMO_TIMESTAMP = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)


class Command(BaseCommand):
    help = "Seed a small Open-FMEA demo vertical slice."

    @transaction.atomic
    def handle(self, *args, **options):
        classic, _ = models.EvaluationDefinition.objects.update_or_create(
            method=CLASSIC_RPN_METHOD,
            defaults={
                "stable_id": "demo:evaluation-definition:classic-rpn",
                "name": "Classic RPN",
                "rating_scales": _default_rating_scales(),
                "configuration": {"formula": "severity * occurrence * detection"},
            },
        )
        ap, _ = models.EvaluationDefinition.objects.update_or_create(
            method=ACTION_PRIORITY_POC_METHOD,
            defaults={
                "stable_id": "demo:evaluation-definition:action-priority-poc",
                "name": "Action Priority PoC Matrix",
                "rating_scales": _default_rating_scales(),
                "configuration": {"variant": "configurable-poc-matrix"},
            },
        )
        ap_real, _ = models.EvaluationDefinition.objects.update_or_create(
            method=AIAG_VDA_AP_METHOD,
            defaults={
                "stable_id": "demo:evaluation-definition:aiag-vda-ap",
                "name": "AIAG & VDA Action Priority (Table AP)",
                "rating_scales": _aiag_vda_rating_scales(),
                "configuration": {
                    "variant": "aiag-vda-handbook-table-ap",
                    "source": "AIAG & VDA FMEA Handbook, 1st Edition, 2019 - Table AP / Tables D1-D3 / P1-P3",
                },
            },
        )
        msr, _ = models.EvaluationDefinition.objects.update_or_create(
            method=AIAG_VDA_MSR_METHOD,
            defaults={
                "stable_id": "demo:evaluation-definition:aiag-vda-msr",
                "name": "AIAG & VDA FMEA-MSR Action Priority (Frequency / Monitoring)",
                "rating_scales": _aiag_vda_msr_rating_scales(),
                "configuration": {
                    "variant": "aiag-vda-msr-handbook-table-ap",
                    "source": "AIAG & VDA FMEA Handbook, 1st Edition, 2019 - Chapter 4, Table MSR2 / Table MSR3 / Table AP (FMEA-MSR)",
                },
            },
        )

        project, _ = models.FMEAProject.objects.update_or_create(
            stable_id="demo:project:brake-assembly",
            defaults={
                "name": "Brake Assembly Launch",
                "description": "Demo project for the first Open-FMEA vertical slice.",
            },
        )
        fmea, _ = models.FMEA.objects.update_or_create(
            stable_id="demo:fmea:brake-assembly-process",
            defaults={
                "project": project,
                "name": "Brake Assembly Process FMEA",
                "description": "Initial process FMEA for assembly risk review.",
                "fmea_type": "process",
                "scope": "Station 20 brake caliper assembly and verification.",
                "lifecycle": FMEALifecycle.IN_REVIEW.value,
                "team": ["Quality Engineer", "Manufacturing Engineer", "Production Lead"],
            },
        )
        product, _ = models.Product.objects.update_or_create(
            stable_id="demo:product:brake-caliper",
            defaults={
                "fmea": fmea,
                "name": "Brake Caliper Assembly",
                "part_number": "BC-DEMO-001",
            },
        )
        process, _ = models.Process.objects.update_or_create(
            stable_id="demo:process:assembly",
            defaults={
                "fmea": fmea,
                "name": "Assembly Process",
                "process_code": "ASM-20",
            },
        )
        operation, _ = models.Operation.objects.update_or_create(
            stable_id="demo:operation:station-20",
            defaults={
                "process": process,
                "name": "Install piston seal",
                "sequence": "20",
            },
        )
        function, _ = models.Function.objects.update_or_create(
            stable_id="demo:function:seal-fluid-pressure",
            defaults={
                "product": product,
                "operation": operation,
                "name": "Maintain hydraulic pressure",
                "description": "Seal must prevent fluid leakage under operating load.",
            },
        )
        requirement, _ = models.Requirement.objects.update_or_create(
            stable_id="demo:requirement:leak-rate",
            defaults={
                "function": function,
                "name": "Leak rate below customer limit",
                "source_reference": "REQ-DEMO-042",
            },
        )
        models.ProductCharacteristic.objects.update_or_create(
            stable_id="demo:characteristic:seal-seat-condition",
            defaults={
                "requirement": requirement,
                "name": "Seal seat surface condition",
                "is_special": True,
                "primary_classification_id": None,
            },
        )
        categories = _seed_default_cause_categories()
        models.ProcessCharacteristic.objects.update_or_create(
            stable_id="demo:process-characteristic:installation-force",
            defaults={
                "operation": operation,
                "name": "Seal installation force",
                "description": "Force applied while seating the piston seal.",
                "cause_category_id": categories["Method"].stable_id,
                "attributes": {
                    "nominal": "controlled manual insertion",
                    "observed": "operator-dependent variation",
                },
            },
        )
        failure_mode, _ = models.FailureMode.objects.update_or_create(
            stable_id="demo:failure-mode:seal-leak",
            defaults={
                "fmea": fmea,
                "function": function,
                "requirement": requirement,
                "name": "Seal leaks after assembly",
                "description": "Piston seal does not hold pressure after final assembly.",
            },
        )
        models.FailureEffect.objects.update_or_create(
            stable_id="demo:effect:loss-of-braking",
            defaults={
                "failure_mode": failure_mode,
                "name": "Reduced braking performance",
            },
        )
        cause, _ = models.FailureCause.objects.update_or_create(
            stable_id="demo:cause:seal-nicked",
            defaults={
                "failure_mode": failure_mode,
                "name": "Seal nicked during installation",
            },
        )
        mechanism, _ = models.FailureMechanism.objects.update_or_create(
            stable_id="demo:mechanism:sharp-edge-contact",
            defaults={
                "failure_cause": cause,
                "name": "Sharp edge contacts seal lip",
            },
        )
        models.PreventionControl.objects.update_or_create(
            stable_id="demo:prevention:chamfer-check",
            defaults={
                "failure_cause": cause,
                "name": "Chamfer verification before assembly",
            },
        )
        detection, _ = models.DetectionControl.objects.update_or_create(
            stable_id="demo:detection:pressure-decay",
            defaults={
                "failure_cause": cause,
                "name": "Pressure decay leak test",
            },
        )
        models.MeasurementMethod.objects.update_or_create(
            stable_id="demo:measurement:leak-tester",
            defaults={
                "detection_control": detection,
                "name": "Automated leak tester",
                "unit": "mbar/min",
            },
        )
        role, _ = models.ResponsibleRole.objects.update_or_create(
            stable_id="demo:role:manufacturing-engineer",
            defaults={"name": "Manufacturing Engineer"},
        )
        action, _ = models.RecommendedAction.objects.update_or_create(
            stable_id="demo:action:add-installation-guide",
            defaults={
                "failure_mode": failure_mode,
                "failure_cause": cause,
                "responsible_role": role,
                "name": "Add seal installation guide fixture",
                "status": ActionStatus.IN_PROGRESS.value,
            },
        )
        models.Evidence.objects.update_or_create(
            stable_id="demo:evidence:fixture-trial",
            defaults={
                "action": action,
                "name": "Fixture trial record",
                "reference_uri": "demo://fixture-trial-001",
            },
        )

        _upsert_cause_influence(
            stable_id="demo:cause-influence:seal-nicked-method",
            source_type="FailureCause",
            source_id=cause.stable_id,
            target_type="FailureMode",
            target_id=failure_mode.stable_id,
            influence_type="produces",
            status=CauseInfluenceStatus.POSSIBLE.value,
            cause_category_id=categories["Method"].stable_id,
            strength="medium",
            source_context="seed_demo",
            review_note="Demo: installation method can damage the seal.",
        )
        _upsert_cause_influence(
            stable_id="demo:cause-influence:sharp-edge-machine",
            source_type="FailureMechanism",
            source_id=mechanism.stable_id,
            target_type="FailureMode",
            target_id=failure_mode.stable_id,
            influence_type="contributes_to",
            status=CauseInfluenceStatus.CORRELATED.value,
            cause_category_id=categories["Machine"].stable_id,
            strength="high",
            evidence_ids=["demo:evidence:fixture-trial"],
            source_context="seed_demo",
            review_note="Demo: fixture trial linked the sharp edge to seal damage.",
        )

        _upsert_cause_influence(
            stable_id="demo:cause-influence:installation-force-seal-seat",
            source_type="ProcessCharacteristic",
            source_id="demo:process-characteristic:installation-force",
            target_type="ProductCharacteristic",
            target_id="demo:characteristic:seal-seat-condition",
            influence_type="affects",
            status=CauseInfluenceStatus.POSSIBLE.value,
            cause_category_id=categories["Method"].stable_id,
            strength="medium",
            source_context="seed_demo",
            review_note="Demo: installation force variation affects the seal seat surface condition.",
        )

        models.RiskEvaluation.objects.filter(failure_mode=failure_mode, actor="seed_demo").delete()
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=classic,
            severity=9,
            occurrence=4,
            detection=5,
            actor="seed_demo",
            trigger="initial-demo-risk",
            stable_id="demo:risk-evaluation:seal-leak:classic-rpn",
            evaluated_at=DEMO_TIMESTAMP,
        )
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=ap,
            severity=9,
            occurrence=4,
            detection=5,
            actor="seed_demo",
            trigger="initial-demo-risk",
            stable_id="demo:risk-evaluation:seal-leak:action-priority",
            evaluated_at=DEMO_TIMESTAMP,
        )
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=ap_real,
            severity=9,
            occurrence=4,
            detection=5,
            actor="seed_demo",
            trigger="initial-demo-risk",
            stable_id="demo:risk-evaluation:seal-leak:aiag-vda-ap",
            evaluated_at=DEMO_TIMESTAMP,
        )
        evaluate_failure_mode(
            failure_mode=failure_mode,
            definition=msr,
            severity=9,
            occurrence=4,  # Frequency (F), not Occurrence - see AIAG_VDA_MSR_METHOD
            detection=5,  # Monitoring (M), not Detection - see AIAG_VDA_MSR_METHOD
            actor="seed_demo",
            trigger="initial-demo-risk",
            stable_id="demo:risk-evaluation:seal-leak:aiag-vda-msr",
            evaluated_at=DEMO_TIMESTAMP,
            failure_scenario="hazardous",
        )

        models.FMEARevision.objects.update_or_create(
            fmea=fmea,
            revision_number=1,
            defaults={
                "stable_id": "demo:revision:brake-assembly-process:001",
                "lifecycle_from": FMEALifecycle.DRAFT.value,
                "lifecycle_to": FMEALifecycle.IN_REVIEW.value,
                "reason": "Initial demo FMEA created for Phase B vertical slice.",
                "actor": "seed_demo",
                "created_at": DEMO_TIMESTAMP,
            },
        )

        # PM-FMEA first increment (Mockup 3): one demo Asset and one demo
        # Preventive FMEA whose failure mode links to it. Maintenance-module
        # concepts the mockup also depicts (WorkOrder, MaintenancePlan, PM
        # Compliance, Baseline/History, Reviews) have no backing entity and
        # are not seeded here.
        imm_03, _ = models.Asset.objects.update_or_create(
            stable_id="demo:asset:imm-03",
            defaults={
                "name": "Injection Molding Machine 03",
                "asset_code": "IMM-03",
                "location": "Plant 1 / Line A",
                "status": models.AssetStatus.OPERATIONAL,
            },
        )
        pm_fmea, _ = models.FMEA.objects.update_or_create(
            stable_id="demo:fmea:injection-molding-pmfmea",
            defaults={
                "project": project,
                "name": "Injection Molding PM-FMEA",
                "description": "Demo Preventive FMEA (PM-FMEA) for the injection molding machine.",
                "fmea_type": "preventive",
                "scope": "Preventive maintenance risk review for IMM-03.",
                "lifecycle": FMEALifecycle.DRAFT.value,
            },
        )
        models.FailureMode.objects.update_or_create(
            stable_id="demo:failure-mode:spindle-bearing-wear",
            defaults={
                "fmea": pm_fmea,
                "name": "Spindle bearing wear",
                "description": "Progressive bearing wear leading to unplanned downtime.",
                "asset": imm_03,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"Seeded demo FMEA: {fmea.stable_id}"))


def _default_rating_scales() -> dict:
    return {
        "severity": {"minimum": 1, "maximum": 10},
        "occurrence": {"minimum": 1, "maximum": 10},
        "detection": {"minimum": 1, "maximum": 10},
    }


def _aiag_vda_rating_scales() -> dict:
    """Real Severity/Occurrence/Detection criteria text for the "aiag-vda-ap"
    EvaluationDefinition, transcribed verbatim from the AIAG & VDA FMEA
    Handbook (1st Ed., 2019), Tables D1-D3 (DFMEA) and P1-P3 (PFMEA). Table
    AP itself (the Action Priority lookup) is code, not data - see
    fmea_evaluation.calculators.calculate_action_priority_aiag_vda. This is
    reference text only, shown alongside the S/O/D input fields; it does not
    change how a rating is calculated.

    DFMEA and PFMEA each have their own wording (PFMEA severity in
    particular is framed across three perspectives), so both are stored
    under one method rather than as two separate EvaluationDefinition rows -
    the underlying Table AP lookup is confirmed cell-for-cell identical for
    both, so only the reference text differs, not the calculation.
    """
    return {
        "source": "AIAG & VDA FMEA Handbook, 1st Edition, 2019 - Tables D1-D3 (DFMEA) / P1-P3 (PFMEA)",
        "dfmea": {
            "severity": {
                "minimum": 1,
                "maximum": 10,
                "bands": {
                    "10": {"label": "Very High", "criteria": "Affects safe operation of the vehicle and/or other vehicles, the health of driver or passenger(s) or road users or pedestrians."},
                    "9": {"label": "Very High", "criteria": "Noncompliance with regulations."},
                    "8": {"label": "High", "criteria": "Loss of primary vehicle function necessary for normal driving during expected service life."},
                    "7": {"label": "High", "criteria": "Degradation of primary vehicle function necessary for normal driving during expected service life."},
                    "6": {"label": "Moderate", "criteria": "Loss of secondary vehicle function."},
                    "5": {"label": "Moderate", "criteria": "Degradation of secondary vehicle function."},
                    "4": {"label": "Moderate", "criteria": "Very objectionable appearance, sound, vibration, harshness, or haptics."},
                    "3": {"label": "Low", "criteria": "Moderately objectionable appearance, sound, vibration, harshness, or haptics."},
                    "2": {"label": "Low", "criteria": "Slightly objectionable appearance, sound, vibration, harshness, or haptics."},
                    "1": {"label": "Very low", "criteria": "No discernible effect."},
                },
            },
            "occurrence": {
                "minimum": 1,
                "maximum": 10,
                "bands": {
                    "10": {"label": "Extremely high", "criteria": "First application of new technology anywhere without operating experience and/or under uncontrolled operating conditions. No product verification and/or validation experience. Standards do not exist and best practices have not yet been determined. Prevention controls not able to predict field performance or do not exist."},
                    "9": {"label": "Very high", "criteria": "First use of design with technical innovations or materials within the company. New application or change in duty cycle / operating conditions. No product verification and/or validation experience. Prevention controls not targeted to identify performance to specific requirements."},
                    "8": {"label": "Very high", "criteria": "First use of design with technical innovations or materials on a new application. New application or change in duty cycle / operating conditions. No product verification and/or validation experience. Few existing standards and best practices, not directly applicable for this design. Prevention controls not a reliable indicator of field performance."},
                    "7": {"label": "High", "criteria": "New design based on similar technology and materials. New application or change in duty cycle / operating conditions. No product verification and/or validation experience. Standards, best practices, and design rules apply to the baseline design, but not the innovations. Prevention controls provide limited indication of performance"},
                    "6": {"label": "High", "criteria": "Similar to previous designs, using existing technology and materials. Similar application, with changes in duty cycle or operating conditions. Previous testing or field experience. Standards and design rules exist but are insufficient to ensure that the failure cause will not occur. Prevention controls provide some ability to prevent a failure cause."},
                    "5": {"label": "Moderate", "criteria": "Detail changes to previous design, using proven technology and materials. Similar application, duty cycle or operating conditions. Previous testing or field experience, or new design with some test experience related to the failure. Design addresses lessons learned from previous designs. Best Practices re-evaluated for this design but have not yet been proven. Prevention controls capable of finding deficiencies in the product related to the failure cause and provide some indication of performance."},
                    "4": {"label": "Moderate", "criteria": "Almost identical design with short-term field exposure. Similar application, with minor change in duty cycle or operating conditions. Previous testing or field experience. Predecessor design and changes for new design conform to best practices, standards, and specifications. Prevention controls capable of finding deficiencies in the product related to the failure cause and indicate likely design conformance."},
                    "3": {"label": "Low", "criteria": "Detail changes to known design (same application, with minor change in duty cycle or operating conditions) and testing or field experience under comparable operating conditions, or new design with successfully completed test procedure. Design expected to conform to Standards and Best Practices, considering Lessons Learned from previous designs. Prevention controls capable of finding deficiencies in the product related to the failure cause and predict conformance of production design."},
                    "2": {"label": "Very low", "criteria": "Almost identical mature design with long term field exposure. Same application, with comparable duty cycle and operating conditions. Testing or field experience under comparable operating conditions. Design expected to conform to standards and best practices, considering Lessons Learned from previous designs, with significant margin of confidence. Prevention controls capable of finding deficiencies in the product related to the failure cause and indicate confidence in design conformance."},
                    "1": {"label": "Extremely low", "criteria": "Failure eliminated through prevention control and failure cause is not possible by design"},
                },
            },
            "detection": {
                "minimum": 1,
                "maximum": 10,
                "bands": {
                    "10": {"label": "Very low", "maturity": "Test procedure yet to be developed.", "opportunity": "Test method not defined"},
                    "9": {"label": "Very low", "maturity": "Test method not designed specifically to detect failure mode or cause.", "opportunity": "Pass-Fail, Test-to-Fail, Degradation Testing"},
                    "8": {"label": "Low", "maturity": "New test method; not proven.", "opportunity": "Pass-Fail, Test-to-Fail, Degradation Testing"},
                    "7": {"label": "Moderate", "maturity": "Proven test method for verification of functionality or validation of performance, quality, reliability and durability; planned timing is later in the product development cycle such that test failures may result in production delays for re-design and/or re-tooling.", "opportunity": "Pass-Fail Testing"},
                    "6": {"label": "Moderate", "maturity": "Proven test method for verification of functionality or validation of performance, quality, reliability and durability; planned timing is later in the product development cycle such that test failures may result in production delays for re-design and/or re-tooling.", "opportunity": "Test-to-Failure"},
                    "5": {"label": "Moderate", "maturity": "Proven test method for verification of functionality or validation of performance, quality, reliability and durability; planned timing is later in the product development cycle such that test failures may result in production delays for re-design and/or re-tooling.", "opportunity": "Degradation Testing"},
                    "4": {"label": "High", "maturity": "Proven test method for verification of functionality or validation of performance, quality, reliability and durability; planned timing is sufficient to modify production tools before release for production.", "opportunity": "Pass-Fail Testing"},
                    "3": {"label": "High", "maturity": "Proven test method for verification of functionality or validation of performance, quality, reliability and durability; planned timing is sufficient to modify production tools before release for production.", "opportunity": "Test-to-Failure"},
                    "2": {"label": "High", "maturity": "Proven test method for verification of functionality or validation of performance, quality, reliability and durability; planned timing is sufficient to modify production tools before release for production.", "opportunity": "Degradation Testing"},
                    "1": {"label": "Very high", "maturity": "Prior testing confirmed that failure mode or cause cannot occur, or detection methods proven to always detect the failure mode or failure cause.", "opportunity": ""},
                },
            },
        },
        "pfmea": {
            "severity": {
                "minimum": 1,
                "maximum": 10,
                "bands": {
                    "10": {"label": "High", "your_plant": "Failure may result in an acute health and/or safety risk for the manufacturing or assembly worker", "ship_to_plant": "Failure may result in an acute health and/or safety risk for the manufacturing or assembly worker", "end_user": "Affects safe operation of the vehicle and/or other vehicles, the health of driver or passenger(s) or road users or pedestrians."},
                    "9": {"label": "High", "your_plant": "Failure may result in in-plant regulatory noncompliance", "ship_to_plant": "Failure may result in in-plant regulatory noncompliance", "end_user": "Noncompliance with regulations."},
                    "8": {"label": "Moderately high", "your_plant": "100% of production run affected may have to be scrapped. Failure may result in in-plant regulatory noncompliance or may have a chronic health and/or safety risk for the manufacturing or assembly worker", "ship_to_plant": "Line shutdown greater than full production shift; stop shipment possible; field repair or replacement required (Assembly to End User) other than for regulatory noncompliance. Failure may result in in-plant regulatory noncompliance or may have a chronic health and/or safety risk for the manufacturing or assembly worker.", "end_user": "Loss of primary vehicle function necessary for normal driving during expected service life."},
                    "7": {"label": "Moderately high", "your_plant": "Product may have to be sorted and a portion (less than 100%) scrapped; deviation from primary process; decreased line speed or added manpower", "ship_to_plant": "Line shutdown from 1 hour up to full production shift; stop shipment possible; field repair or replacement required (Assembly to End User) other than for regulatory noncompliance", "end_user": "Degradation of primary vehicle function necessary for normal driving during expected service life."},
                    "6": {"label": "Moderately low", "your_plant": "100% of production run may have to be reworked off line and accepted", "ship_to_plant": "Line shutdown up to one hour", "end_user": "Loss of secondary vehicle function."},
                    "5": {"label": "Moderately low", "your_plant": "A portion of the production run may have to be reworked off line and accepted", "ship_to_plant": "Less than 100% of product affected; strong possibility for additional defective product; sort required; no line shutdown", "end_user": "Degradation of secondary vehicle function."},
                    "4": {"label": "Low", "your_plant": "100% of production run may have to be reworked in station before it is processed", "ship_to_plant": "Defective product triggers significant reaction plan; additional defective products not likely; sort not required", "end_user": "Very objectionable appearance, sound, vibration, harshness, or haptics."},
                    "3": {"label": "Low", "your_plant": "A portion of the production run may have to be reworked in-station before it is processed", "ship_to_plant": "Defective product triggers minor reaction plan; additional defective products not likely; sort not required", "end_user": "Moderately objectionable appearance, sound, vibration, harshness, or haptics."},
                    "2": {"label": "Low", "your_plant": "Slight inconvenience to process, operation, or operator", "ship_to_plant": "Defective product triggers no reaction plan; additional defective products not likely; sort not required; requires feedback to supplier", "end_user": "Slightly objectionable appearance, sound, vibration, harshness, or haptics."},
                    "1": {"label": "Very low", "your_plant": "No discernible effect", "ship_to_plant": "No discernible effect or no effect", "end_user": "No discernible effect."},
                },
            },
            "occurrence": {
                "minimum": 1,
                "maximum": 10,
                "bands": {
                    "10": {"label": "Extremely high", "type_of_control": "None", "criteria": "No prevention controls."},
                    "9": {"label": "Very high", "type_of_control": "Behavioral", "criteria": "Prevention controls will have little effect in preventing failure cause."},
                    "8": {"label": "Very high", "type_of_control": "Behavioral", "criteria": "Prevention controls will have little effect in preventing failure cause."},
                    "7": {"label": "High", "type_of_control": "Behavioral or Technical", "criteria": "Prevention controls somewhat effective in preventing failure cause."},
                    "6": {"label": "High", "type_of_control": "Behavioral or Technical", "criteria": "Prevention controls somewhat effective in preventing failure cause."},
                    "5": {"label": "Moderate", "type_of_control": "Behavioral or Technical", "criteria": "Prevention controls are effective in preventing failure cause."},
                    "4": {"label": "Moderate", "type_of_control": "Behavioral or Technical", "criteria": "Prevention controls are effective in preventing failure cause."},
                    "3": {"label": "Low", "type_of_control": "Best Practices: Behavioral or Technical", "criteria": "Prevention controls are highly effective in preventing failure cause."},
                    "2": {"label": "Very low", "type_of_control": "Best Practices: Behavioral or Technical", "criteria": "Prevention controls are highly effective in preventing failure cause."},
                    "1": {"label": "Extremely low", "type_of_control": "Technical", "criteria": "Prevention controls are extremely effective in preventing failure cause from occurring due to design (e.g. part geometry) or process (e.g. fixture or tooling design). Intent of prevention controls - Failure Mode cannot be physically produced due to the Failure Cause."},
                },
            },
            "detection": {
                "minimum": 1,
                "maximum": 10,
                "bands": {
                    "10": {"label": "Very low", "maturity": "No testing or inspection method has been established or is known.", "opportunity": "The failure mode will not or cannot be detected."},
                    "9": {"label": "Very low", "maturity": "It is unlikely that the testing or inspection method will detect the failure mode.", "opportunity": "The failure mode is not easily detected through random or sporadic audits."},
                    "8": {"label": "Low", "maturity": "Test or inspection method has not been proven to be effective and reliable (e.g. plant has little or no experience with method, gauge R&R results marginal on comparable process or this application, etc.).", "opportunity": "Human inspection (visual, tactile, audible), or use of manual gauging (attribute or variable) that should detect the failure mode or failure cause."},
                    "7": {"label": "Low", "maturity": "Test or inspection method has not been proven to be effective and reliable (e.g. plant has little or no experience with method, gauge R&R results marginal on comparable process or this application, etc.).", "opportunity": "Machine-based detection (automated or semi-automated with notification by light, buzzer, etc.), or use of inspection equipment such as a coordinate measuring machine that should detect failure mode or failure cause."},
                    "6": {"label": "Moderate", "maturity": "Test or inspection method has been proven to be effective and reliable (e.g. plant has experience with method; gauge R&R results are acceptable on comparable process or this application, etc.).", "opportunity": "Human inspection (visual, tactile, audible), or use of manual gauging (attribute or variable) that will detect the failure mode or failure cause (including product sample checks)."},
                    "5": {"label": "Moderate", "maturity": "Test or inspection method has been proven to be effective and reliable (e.g. plant has experience with method; gauge R&R results are acceptable on comparable process or this application, etc.).", "opportunity": "Machine-based detection (semi-automated with notification by light, buzzer, etc.), or use of inspection equipment such as a coordinate measuring machine that will detect failure mode or failure cause (including product sample checks)."},
                    "4": {"label": "High", "maturity": "System has been proven to be effective and reliable (e.g. plant has experience with method on identical process or this application), gauge R&R results are acceptable, etc.", "opportunity": "Machine-based automated detection method that will detect the failure mode downstream, prevent further processing or system will identify the product as discrepant and allow it to automatically move forward in the process until the designated reject unload area. Discrepant product will be controlled by a robust system that will prevent outflow of the product from the facility."},
                    "3": {"label": "High", "maturity": "System has been proven to be effective and reliable (e.g. plant has experience with method on identical process or this application), gauge R&R results are acceptable, etc.", "opportunity": "Machine-based automated detection method that will detect the failure mode in-station, prevent further processing or system will identify the product as discrepant and allow it to automatically move forward in the process until the designated reject unload area. Discrepant product will be controlled by a robust system that will prevent outflow of the product from the facility."},
                    "2": {"label": "High", "maturity": "Detection method has been proven to be effective and reliable (e.g. plant has experience with method, error-proofing verifications, etc.).", "opportunity": "Machine-based detection method that will detect the cause and prevent the failure mode (discrepant part) from being produced."},
                    "1": {"label": "Very high", "maturity": "Failure mode cannot be physically produced as-designed or processed, or detection methods proven to always detect the failure mode or failure cause.", "opportunity": ""},
                },
            },
        },
    }


def _seed_default_cause_categories() -> dict[str, models.CauseCategory]:
    scheme, _ = models.CauseCategoryScheme.objects.update_or_create(
        stable_id=DEFAULT_SCHEME_STABLE_ID,
        defaults={
            "name": "Ishikawa 5M+E (default)",
            "description": "Default configurable cause-category scheme for Ishikawa review.",
        },
    )
    categories: dict[str, models.CauseCategory] = {}
    for stable_id, name, description, sort_order in DEFAULT_CATEGORIES:
        category, _ = models.CauseCategory.objects.update_or_create(
            stable_id=stable_id,
            defaults={
                "scheme_id": scheme.stable_id,
                "name": name,
                "description": description,
                "sort_order": sort_order,
            },
        )
        categories[name] = category
    return categories


def _upsert_cause_influence(
    *,
    stable_id: str,
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    influence_type: str,
    status: str,
    cause_category_id: str,
    strength: str,
    source_context: str,
    review_note: str,
    evidence_ids: list[str] | None = None,
) -> models.CauseInfluence:
    influence, _ = models.CauseInfluence.objects.update_or_create(
        stable_id=stable_id,
        defaults={
            "source_type": source_type,
            "source_id": source_id,
            "target_type": target_type,
            "target_id": target_id,
            "influence_type": influence_type,
            "status": status,
            "cause_category_id": cause_category_id,
            "strength": strength,
            "source_context": source_context,
            "review_note": review_note,
            "evidence_ids": evidence_ids or [],
        },
    )
    influence.full_clean()
    return influence


def _aiag_vda_msr_rating_scales() -> dict:
    """Real Frequency (F) / Monitoring (M) criteria text plus the Failure
    Scenario category descriptions for the "aiag-vda-msr" EvaluationDefinition,
    transcribed verbatim from the AIAG & VDA FMEA Handbook (1st Ed., 2019),
    Chapter 4 (Supplemental FMEA for Monitoring and System Response):
    Table MSR2 (Frequency), Table MSR3 (Monitoring), and section 4.4.2
    (Failure Scenario). Table AP itself (the FMEA-MSR Action Priority
    lookup) is code, not data - see
    fmea_evaluation.calculators.calculate_action_priority_msr. This is
    reference text only, shown alongside the S/F/M input fields; it does
    not change how a rating is calculated.

    FMEA-MSR reuses the same Severity scale as DFMEA (see the "aiag-vda-ap"
    EvaluationDefinition's "dfmea" severity bands) - only Frequency and
    Monitoring are new here, replacing Occurrence and Detection.
    """
    return {
        "source": "AIAG & VDA FMEA Handbook, 1st Edition, 2019 - Chapter 4, Table MSR2 / Table MSR3 / Table AP (FMEA-MSR)",
        "failure_scenario": {
            "non_hazardous": (
                "Failure Scenario (1) - Non-Hazardous: describes the malfunctioning behavior "
                "from the occurrence of the fault to the Failure Effect, which is not hazardous "
                "but may reach a non-compliant end system state."
            ),
            "hazardous": (
                "Failure Scenario (2) - Hazardous: describes the malfunctioning behavior from "
                "the occurrence of the fault to the Failure Effect, which leads to a hazardous "
                "event. The Fault Handling Time Interval is the maximum time span of "
                "malfunctioning behavior before a hazardous event occurs, if the safety "
                "mechanisms are not activated."
            ),
            "mitigated": (
                "Failure Scenario (3) - Mitigated (Effect): describes the malfunctioning "
                "behavior from the occurrence of the fault to the mitigated Failure Effect, "
                "which leads to a loss or degradation of a function instead of the hazardous "
                "event."
            ),
        },
        "frequency": {
            "minimum": 1,
            "maximum": 10,
            "bands": {
                "10": {"label": "Extremely high or cannot be determined", "criteria": "Frequency of occurrence of the Failure Cause is unknown or known to be unacceptably high during the intended service life of the vehicle"},
                "9": {"label": "High", "criteria": "Failure Cause is likely to occur during the intended service life of the vehicle"},
                "8": {"label": "High", "criteria": "Failure Cause may occur often in the field during the intended service life of the vehicle"},
                "7": {"label": "High", "criteria": "Failure Cause may occur frequently in the field during the intended service life of the vehicle"},
                "6": {"label": "Medium", "criteria": "Failure Cause may occur somewhat frequently in the field during the intended service life of the vehicle"},
                "5": {"label": "Medium", "criteria": "Failure Cause may occur occasionally in the field during the intended service life of the vehicle."},
                "4": {"label": "Low", "criteria": "Failure Cause is predicted to occur rarely in the field during the intended service life of the vehicle. At least ten occurrences in the field are predicted."},
                "3": {"label": "Very low", "criteria": "Failure Cause is predicted to occur in isolated cases in the field during the intended service life of the vehicle. At least one occurrence in the field is predicted."},
                "2": {"label": "Extremely low", "criteria": "Failure Cause is predicted not to occur in the field during the intended service life of the vehicle based on prevention and detection controls and field experience with similar parts. Isolated cases cannot be ruled out. No proof it will not happen."},
                "1": {"label": "Cannot Occur", "criteria": "Failure Cause cannot occur during the intended service life of the vehicle or is virtually eliminated. Evidence that Failure Cause cannot occur. Rationale is documented."},
            },
            "exposure_time_reduction": [
                {"operating_time_percentage": "< 10%", "reduce_frequency_by": 1},
                {"operating_time_percentage": "< 1%", "reduce_frequency_by": 2},
            ],
        },
        "monitoring": {
            "minimum": 1,
            "maximum": 10,
            "combination_rule": "Use the rating number that corresponds with the least effective of either criteria for Monitoring or System Response",
            "bands": {
                "10": {"label": "Not effective", "diagnostic_monitoring": "The fault/failure cannot be detected at all or not during the Fault Handling Time Interval; by the system, the driver, a passenger, or service technician.", "system_response": "No response during the Fault Handling Time Interval."},
                "9": {"label": "Very Low", "diagnostic_monitoring": "The fault/failure can almost never be detected in relevant operating conditions. Monitoring control with low effectiveness, high variance, or high uncertainty. Minimal diagnostic coverage.", "system_response": "The reaction to the fault/failure by the system or the driver may not reliably occur during the Fault Handling Time Interval."},
                "8": {"label": "Low", "diagnostic_monitoring": "The fault/failure can be detected in very few relevant operating conditions. Monitoring control with low effectiveness, high variance, or high uncertainty. Diagnostic coverage estimated <60%.", "system_response": "The reaction to the fault/failure by the system or the driver may not always occur during the Fault Handling Time Interval."},
                "7": {"label": "Moderately Low", "diagnostic_monitoring": "Low probability of detecting the fault/failure during the Fault Handling Time Interval by the system or the driver. Monitoring control with low effectiveness, high variance, or high uncertainty. Diagnostic coverage estimated >60%.", "system_response": "Low probability of reacting to the detected fault/failure during the Fault Handling Time Interval by the system or the driver."},
                "6": {"label": "Moderate", "diagnostic_monitoring": "The fault/failure will be automatically detected by the system or the driver only during power-up, with medium variance in detection time. Diagnostic coverage estimated >90%.", "system_response": "The automated system or the driver will be able to react to the detected fault/failure in many operating conditions."},
                "5": {"label": "Moderate", "diagnostic_monitoring": "The fault/failure will be automatically detected by the system during the Fault Handling Time Interval, with medium variance in detection time, or detected by the driver in very many operating conditions. Diagnostic coverage estimated between 90% - 97%.", "system_response": "The automated system or the driver will be able to react to the detected fault/failure during the Fault Handling Time Interval in very many operating conditions."},
                "4": {"label": "Moderately High", "diagnostic_monitoring": "The fault/failure will be automatically detected by the system during the Fault Handling Time Interval, with medium variance in detection time, or detected by the driver in most operating conditions. Diagnostic coverage estimated >97%.", "system_response": "The automated system or the driver will be able to react to the detected fault/failure during the Fault Handling Time interval, in most operating conditions."},
                "3": {"label": "High", "diagnostic_monitoring": "The fault/failure will be automatically detected by the system during the Fault Handling Time Interval with very low variance in detection time, and with a high probability. Diagnostic coverage estimated >99%.", "system_response": "The system will automatically react to the detected fault/failure during the Fault Handling Time Interval in most operating conditions with very low variance in system response time, and with a high probability."},
                "2": {"label": "Very High", "diagnostic_monitoring": "The fault/failure will be detected automatically by the system with very low variance in detection time during the Fault Handling Time Interval, and with a very high probability. Diagnostic coverage estimated > 99.9%.", "system_response": "The system will automatically react to the detected fault/failure during the Fault Handling Time Interval with very low variance in system response time, and with a very high probability."},
                "1": {"label": "Reliable and acceptable for elimination of original Failure Effect.", "diagnostic_monitoring": "The fault/failure will always be detected automatically by the system. Diagnostic coverage estimated to be significantly greater than 99.9%.", "system_response": "The system will always automatically react to the detected fault/failure during the Fault Handling Time Interval."},
            },
        },
        "not_yet_implemented": (
            "Handbook NOTE 1/NOTE 2 (Table AP for FMEA-MSR, p. 148): when Monitoring=1, the "
            "mitigated Failure Effect's severity replaces the original Failure Effect's severity "
            "for this AP lookup and for the parent DFMEA's own AP lookup. Not implemented in this "
            "increment - see fmea_evaluation.calculators module comment above "
            "calculate_action_priority_msr."
        ),
    }
