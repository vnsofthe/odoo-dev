_error_msg_history = '本工具不能用于有乳腺导管内原位癌或者乳腺原位小叶癌用药史的女性乳腺癌风险精准预测';
_error_msg_genetics = '其他的工具可能更加适合于BRCA1/BRCA2突变的女性或者患有其他能够增加乳腺癌风险的遗传性综合征的女性的乳腺癌风险预测.'
_error_msg_current_age = "本工具只适用于35岁及以上的女性的乳腺癌风险预测。";
_error_msg_hist_age = "本工具不能用于有乳腺导管内原位癌或者乳腺原位小叶癌用药史的女性乳腺癌风险精准预测，而且只预测35岁及以上的女性的乳腺癌风险。";
function checkAge() {
    if (document.risk.current_age.selectedIndex == 1)
        alert(_error_msg_current_age);
}
function checkHistory() {
    if (document.risk.history.selectedIndex == 1)
        alert(_error_msg_history);
}
function checkGenetics() {
    if (document.risk.genetics.selectedIndex == 1)
        alert(_error_msg_genetics);
}
function checkEthnicity() {
    if (document.risk.race.selectedIndex == 2) {
        //alert("Assessments for African American women may underestimate the chance of breast cancer and are subject to greater uncertainty than those for white women. Researchers are conducting additional studies, including studies with minority populations, to gather more data and to increase the accuracy of the tool for women in these populations."); 
        //dec282007 SRamaiah: this has been removed as the new model(CARE) is now in use for african american women
    }
    else if (document.risk.race.selectedIndex == 3)
    { alert("本工具评估西班牙裔女性相比白人和非洲裔美国女性有更大的不确定性。研究人员正在进行更多的研究,包括少数族裔的研究,以收集更多的数据来增加本工具对此部分人群风险预测的准确性。"); }
    //else if (document.risk.race.selectedIndex == 4) {    
    //{ alert("Assessments for Asian or Pacific Islander women are uncertain and are based on data for white women. Researchers are conducting additional studies, including studies with minority populations, to gather more data and to increase the accuracy of the tool for women in these populations."); }    
    else if (document.risk.race.selectedIndex == 5)
    { alert("本工具基于白人女性数据，评估美国印第安人或阿拉斯加土著女性具有更大的不确定性。研究人员正在进行更多的研究,包括少数族裔的研究,以收集更多的数据来增加本工具对此部分人群风险预测的准确性。"); }
    else if (document.risk.race.selectedIndex == 6)
    { alert("本工具是基于白人女性数据进行风险评估。"); }
    //reset it to white female
    //document.risk.race.selectedIndex=1;

    //Populate sub race/ehnicity
    if (document.risk.race.selectedIndex != 4) {
        document.risk.subrace.options.length = 0;
        document.risk.subrace.options[0] = new Option("n/a");
        document.risk.subrace.selectedIndex = 0;
        document.risk.subrace.options[0].value = 99;
    }
    else {
        document.risk.subrace.options[0] = new Option("请选择");
        document.risk.subrace.options[0].value = 999;
        document.risk.subrace.options[1] = new Option("中国人");
        document.risk.subrace.options[1].value = 7;
        document.risk.subrace.options[2] = new Option("日本人");
        document.risk.subrace.options[2].value = 8;
        document.risk.subrace.options[3] = new Option("菲律宾人");
        document.risk.subrace.options[3].value = 9;
        document.risk.subrace.options[4] = new Option("夏威夷岛人");
        document.risk.subrace.options[4].value = 10;
        document.risk.subrace.options[5] = new Option("其他太平洋岛人");
        document.risk.subrace.options[5].value = 11;
        document.risk.subrace.options[6] = new Option("其他");
        document.risk.subrace.options[6].value = 12;
        document.risk.subrace.selectedIndex = 0;
    }
}

function checkBiopsy() {
    if (document.risk.ever_had_biopsy.selectedIndex == 1) { // Unknown
        document.risk.previous_biopsies.options.length = 0;
        document.risk.previous_biopsies.options[0] = new Option("n/a");
        document.risk.previous_biopsies.selectedIndex = 0;
        document.risk.previous_biopsies.options[0].value = 99;
        document.risk.biopsy_with_hyperplasia.options.length = 0;
        document.risk.biopsy_with_hyperplasia.options[0] = new Option("n/a");
        document.risk.biopsy_with_hyperplasia.selectedIndex = 0;
        document.risk.biopsy_with_hyperplasia.options[0].value = 99;
    }
    if (document.risk.ever_had_biopsy.selectedIndex == 2) { // No
        document.risk.previous_biopsies.options.length = 0;
        document.risk.previous_biopsies.options[0] = new Option("n/a");
        document.risk.previous_biopsies.selectedIndex = 0;
        document.risk.previous_biopsies.options[0].value = 0;
        document.risk.biopsy_with_hyperplasia.options.length = 0;
        document.risk.biopsy_with_hyperplasia.options[0] = new Option("n/a");
        document.risk.biopsy_with_hyperplasia.selectedIndex = 0;
        document.risk.biopsy_with_hyperplasia.options[0].value = 0;
    }
    if (document.risk.ever_had_biopsy.selectedIndex == 3) { // Yes
        document.risk.previous_biopsies.options[0] = new Option("请选择");
        document.risk.previous_biopsies.options[0].value = 999;
        document.risk.previous_biopsies.options[1] = new Option("1");
        document.risk.previous_biopsies.options[1].value = 1;
        document.risk.previous_biopsies.options[2] = new Option("> 1");
        document.risk.previous_biopsies.options[2].value = 2;
        document.risk.previous_biopsies.selectedIndex = 0;
        document.risk.biopsy_with_hyperplasia.options[0] = new Option("请选择");
        document.risk.biopsy_with_hyperplasia.options[0].value = 999;
        document.risk.biopsy_with_hyperplasia.options[1] = new Option("未知");
        document.risk.biopsy_with_hyperplasia.options[1].value = 99;
        document.risk.biopsy_with_hyperplasia.options[2] = new Option("否");
        document.risk.biopsy_with_hyperplasia.options[2].value = 0;
        document.risk.biopsy_with_hyperplasia.options[3] = new Option("是");
        document.risk.biopsy_with_hyperplasia.options[3].value = 1;
        document.risk.biopsy_with_hyperplasia.selectedIndex = 0;
        //    document.reload();
    }
}
function calculate() {


    if (document.risk.history.selectedIndex == 0 ||
      document.risk.genetics.selectedIndex == 0 ||
      document.risk.current_age.selectedIndex == 0 ||
      document.risk.age_at_menarche.selectedIndex == 0 ||
      document.risk.age_at_first_live_birth.selectedIndex == 0 ||
      document.risk.related_with_breast_cancer.selectedIndex == 0 ||
      document.risk.ever_had_biopsy.selectedIndex == 0 ||
      document.risk.ever_had_biopsy.selectedIndex == 3 && document.risk.previous_biopsies.selectedIndex == 0 ||
      document.risk.ever_had_biopsy.selectedIndex == 3 && document.risk.biopsy_with_hyperplasia.selectedIndex == 0 ||
      document.risk.race.selectedIndex == 4 && document.risk.subrace.selectedIndex == 0 ||
      document.risk.race.selectedIndex == 0) {
        alert("请先选择所有问题的答案，再进行风险计算.");
        return;
    }
    else if (document.risk.current_age.selectedIndex == 1 && document.risk.history.selectedIndex == 1) {
        alert(_error_msg_hist_age);
        return;
    }
    else if (document.risk.history.selectedIndex == 1) {
        alert(_error_msg_history);
        return;
    }
    else if (document.risk.genetics.selectedIndex == 1) {
        alert(_error_msg_genetics);
        return;
    }
    else if (document.risk.current_age.selectedIndex == 1) {
        alert(_error_msg_current_age);
        return;
    }

    genetics = document.risk.genetics.options[document.risk.genetics.selectedIndex].value;
    current_age = document.risk.current_age.options[document.risk.current_age.selectedIndex].value;
    age_at_menarche = document.risk.age_at_menarche.options[document.risk.age_at_menarche.selectedIndex].value;
    age_at_first_live_birth = document.risk.age_at_first_live_birth.options[document.risk.age_at_first_live_birth.selectedIndex].value;
    ever_had_biopsy = document.risk.ever_had_biopsy.options[document.risk.ever_had_biopsy.selectedIndex].value;
    previous_biopsies = document.risk.previous_biopsies.options[document.risk.previous_biopsies.selectedIndex].value;
    biopsy_with_hyperplasia = document.risk.biopsy_with_hyperplasia.options[document.risk.biopsy_with_hyperplasia.selectedIndex].value;
    related_with_breast_cancer = document.risk.related_with_breast_cancer.options[document.risk.related_with_breast_cancer.selectedIndex].value;
    if (document.risk.race.selectedIndex == 4) {
        race = document.risk.subrace.options[document.risk.subrace.selectedIndex].value;
    }
    else {
        race = document.risk.race.options[document.risk.race.selectedIndex].value;

    }

    if (document.risk.race.selectedIndex == 4)
        asian = "It has been observed that recent immigrants from rural Asia may have a lower risk of breast cancer than calculated.";
    else
        asian = "";

    if (previous_biopsies == "")
        previous_biopsies = "99";
    if (biopsy_with_hyperplasia == "")
        biopsy_with_hyperplasia = "99";

    parameters = {"genetics":genetics,
				 "current_age":current_age,
				 "age_at_menarche":age_at_menarche,
				 "age_at_first_live_birth":age_at_first_live_birth,
				 "ever_had_biopsy":ever_had_biopsy,
				 "previous_biopsies": previous_biopsies,
				 "biopsy_with_hyperplasia":biopsy_with_hyperplasia,
				 "related_with_breast_cancer":related_with_breast_cancer,
				 "race":race}
	if(asian!=""){
		parameters["asian"]=asian
	}

    return parameters;
}

function disclaimer() {
    if (document.risk.race.selectedIndex == 0 || document.risk.race.selectedIndex == 1) {
        document.risk.dText.value = "";
    }
    else if (document.risk.race.selectedIndex == 2) {
        document.risk.dText.value = "The projections for African American women may slightly underestimate the likelihood of breast cancer and are subject to greater uncertainty than those for white women.";
    }
    else if (document.risk.race.selectedIndex == 3) {
        document.risk.dText.value = "The projections for Hispanic women are subject to greater uncertainty than those for white women.";
    }
    else if (document.risk.race.selectedIndex == 4) {
        document.risk.dText.value = "Calculations for Asian or Pacific Islander women are based on the rates for white women and are uncertain.";
    }
    else if (document.risk.race.selectedIndex == 5) {
        document.risk.dText.value = "Calculations for American Indian or Alaskan Native women are based on the rates for white women and are uncertain.";
    }
    else if (document.risk.race.selectedIndex == 6) {
        document.risk.dText.value = "If the patient's race is unknown, the program will use data for white females to estimate the predicted risk.";
    }
}
