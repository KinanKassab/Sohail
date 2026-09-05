import math
import random


class MonthlyTumorSimulation:
    def __init__(self):
        # معاملات النموذج الأساسية - يتم تعديلها من الواجهة
        self.G_S = 0.0250
        self.G_R = 0.0150
        self.G_D = 0.0020
        self.T = 0.0015
        self.gamma = 0.0010
        self.delta = 0.0005
        self.I = 0.30
        self.C = 0.04
        self.L_R = 0.10
        self.alpha = 0.8
        self.beta = 1.2
        self.K = 15.0
        self.ME = 0.015
        self.C_G_I = 0.12
        self.N_G_I = 0.03
        self.G_T_G_I = 0.004
        self.MC = 0.2
        self.EC50 = 0.04
        self.n_hill = 2.0

        # القيم الابتدائية - يتم تعديلها من الواجهة
        self.S_initial = 4.0
        self.R_initial = 2.0
        self.D_initial = 4.0

        # إعدادات المحاكاة
        self.simulation_days = 30
        self.dose_days = [1, 8, 15, 22]
        self.dose_amount = 0.04
        self.pink_intensity = 0.0

        # متغيرات التشغيل
        self.S = 0.0
        self.R = 0.0
        self.D = 0.0
        self.day = 0
        self.history = []

        # معاملات المقاومة المصححة
        self.alpha_res = 0.0005
        self.beta_res = 0.015
        self.gamma_res = 0.005
        self.delta_res = 0.3
        self.epsilon_res = 0.1
        self.mu_res = 0.2
        self.tau_res = 5
        self.noise_factor = 0.005
        self.delay_buffer = [0.0] * self.tau_res

        # تحلل تأثير الكيميائي
        self.chemo_decay_schedule = {0: 1.0, 1: 0.75, 2: 0.25, 3: 0.0}
        self.days_since_dose = 99
        self.chemo_effect = 0.0

        # معاملات إضافية
        self.D_to_S_rate = 0.015
        self.D_to_R_rate = 0.010
        self.stem_activation_threshold = 2.0
        self.resistance_factor = 1.0

    @staticmethod
    def hill_effect(concentration, ec50, n):
        if concentration <= 0:
            return 0.0
        return (concentration**n) / (concentration**n + ec50**n)

    def get_growth_factor(self, total_tumor):
        if total_tumor <= 0:
            return 1.0
        ratio = total_tumor / self.K
        gf = 1.0 / (1.0 + math.exp(4 * (ratio - 0.5)))
        if total_tumor < 3.0:
            boost = 4.0 * (1 - total_tumor / 3.0)
            gf *= 1 + boost
        elif total_tumor > 10.0:
            denominator = max(self.K - 10.0, 1e-9)
            penalty = 0.3 * (total_tumor - 10.0) / denominator
            gf *= 1 - penalty * 0.5
        return max(0.2, min(5.0, gf))

    def calculate_tumor_hypoxia_factor(self, total_tumor):
        if total_tumor <= 0:
            return 1.0
        ratio = total_tumor / self.K
        hf = 1.0 / (1.0 + math.exp(-6 * (ratio - 0.5)))
        return max(0.1, min(0.95, hf))

    def calculate_tumor_treatment_resistance(self, total_tumor):
        if total_tumor <= 0:
            return 1.0
        ratio = total_tumor / self.K
        return 1.0 + 2.0 * (ratio**1.5)

    def calculate_dR_corrected(self, S, R, D, C, I, L_R, K, delay_buffer):
        spontaneous = self.alpha_res * S
        growth = self.beta_res * R * (1 + R / K)
        activation = self.gamma_res * delay_buffer[0]
        immune = (self.delta_res * I * R) / (1 + I * R)
        nutrition = (self.epsilon_res * L_R * R) / (1 + L_R)
        hill_treatment = self.hill_effect(C, self.EC50, self.n_hill)
        selective_pressure = (self.mu_res * S * hill_treatment) / (1 + C)
        noise = R * self.noise_factor * random.uniform(-1, 1)
        dR = spontaneous + growth + activation - immune - nutrition + selective_pressure + noise
        return max(0.0, dR)

    def update_chemo_effect(self, is_dose_day):
        if is_dose_day:
            self.days_since_dose = 0
            self.chemo_effect = self.chemo_decay_schedule[0]
        else:
            self.days_since_dose += 1
            self.chemo_effect = self.chemo_decay_schedule.get(self.days_since_dose, 0.0)
        return self.chemo_effect

    def reset_simulation(self):
        """إعادة تعيين المحاكاة للبدء من جديد."""
        self.S = self.S_initial
        self.R = self.R_initial
        self.D = self.D_initial
        self.I = 0.30
        self.day = 0
        self.history = []
        self.days_since_dose = 99
        self.chemo_effect = 0.0
        self.delay_buffer = [0.0] * self.tau_res

    def run_simulation(self):
        """تشغيل المحاكاة بالكامل وإرجاع النتائج."""
        self.reset_simulation()

        if self.pink_intensity > 0:
            self.apply_pink_environment(self.pink_intensity)

        results = []

        for day in range(1, self.simulation_days + 1):
            is_dose_day = day in self.dose_days

            S_old, R_old, D_old = self.S, self.R, self.D
            total_old = S_old + R_old + D_old

            growth_factor = self.get_growth_factor(total_old)
            C_current = self.dose_amount if is_dose_day else 0.0

            chemo_effect = self.update_chemo_effect(is_dose_day)
            hypoxia = self.calculate_tumor_hypoxia_factor(total_old)
            tumor_resistance = self.calculate_tumor_treatment_resistance(total_old)

            treatment_S = self.hill_effect(C_current, self.EC50, self.n_hill)
            dS = S_old * (
                treatment_S
                - self.I
                - self.T * self.resistance_factor
                - self.L_R
                + self.G_S * growth_factor
            )
            S_new = max(0.005, S_old + dS)

            dR = self.calculate_dR_corrected(
                S_old,
                R_old,
                D_old,
                C_current,
                self.I,
                self.L_R,
                self.K,
                self.delay_buffer,
            )
            R_new = max(0.005, R_old + dR)

            dD = (
                self.G_D * D_old * growth_factor
                + self.gamma * S_old
                - self.delta * D_old
            )
            D_new = max(0.005, D_old + dD)

            natural_boost = (
                self.ME * total_old * 0.5
                + self.N_G_I * self.L_R * 0.5
                + self.G_T_G_I * total_old * 0.3
            )
            chemo_suppression = self.C_G_I * self.hill_effect(chemo_effect, 0.5, 2.0)
            dI = natural_boost - chemo_suppression + self.L_R * 0.1
            I_new = max(0.05, min(1.2, self.I + dI))

            self.S, self.R, self.D, self.I = S_new, R_new, D_new, I_new
            total_new = S_new + R_new + D_new

            if total_new > self.K:
                scale = self.K / total_new
                self.S *= scale
                self.R *= scale
                self.D *= scale

            self.delay_buffer = [dR] + self.delay_buffer[:-1]

            results.append(
                {
                    "day": day,
                    "S": round(self.S, 4),
                    "R": round(self.R, 4),
                    "D": round(self.D, 4),
                    "total": round(self.S + self.R + self.D, 4),
                    "I": round(self.I, 4),
                    "is_dose_day": is_dose_day,
                    "chemo_effect": round(chemo_effect, 4),
                    "hypoxia": round(hypoxia, 4),
                    "resistance": round(tumor_resistance, 4),
                }
            )

        self.history = results
        return results

    def apply_pink_environment(self, intensity=1.0):
        """تطبيق البيئة الوردية."""
        ph_boost = 1.0 + 0.3 * intensity
        nutrient_boost = 1.0 + 0.5 * intensity
        x_activation = 0.02 * intensity
        self.G_S *= nutrient_boost
        self.G_R /= ph_boost
        self.T += x_activation
