# 1. Tag group experiment
- Generate movie samples

      cd tag_group
      sh gen_movies.sh
- Launch HITs

      cd ${PROJECT_ROOT}
      sh launch.sh tag_group ${EXPT_ID} --prod

- Check progress

      python show_hit_progress.py --hit_ids_file=tag_group/${ID_FILE} --prod

- Retrieve results
      python get_results.py   --hit_ids_file=tag_group/${ID_FILE} > tag_group/${RESULT} --prod

# 2. Tag explanation experiment
- Generate input file to HIT template

      cd tag_explanation
      sh gen_input.sh ${EXPT_ID}

- Launch HITs

      cd ${PROJECT_ROOT}
      python launch_hits.py   --html_template=tag_group.html   --hit_properties_file=hit_properties/tag_group.json   --input_json_file=tag_group/${INPUT}  --hit_ids_file=tag_group/${ID_FILE}
