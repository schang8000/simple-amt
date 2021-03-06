import argparse, json
import simpleamt

if __name__ == '__main__':
  parser = argparse.ArgumentParser(parents=[simpleamt.get_parent_parser()])
  args = parser.parse_args()
  mtc = simpleamt.get_mturk_connection_from_args(args)

  approve_ids = []
  reject_ids = []

  if args.hit_ids_file is None:
    parser.error('Must specify --hit_ids_file.')

  with open(args.hit_ids_file, 'r') as f:
    hit_ids = [line.strip() for line in f]

  for hit_id in hit_ids:
    for a in mtc.get_assignments(hit_id):
      print a.AssignmentStatus
      if a.AssignmentStatus == 'Submitted':
        try:
          # Try to parse the output from the assignment. If it isn't
          # valid JSON then we reject the assignment.
          output = json.loads(a.answers[0][0].fields[0])
          approve_ids.append(a.AssignmentId)
        except ValueError as e:
          reject_ids.append(a.AssignmentId)

  print ('This will approve %d assignments and reject %d assignments with '
         'sandbox=%s' % (len(approve_ids), len(reject_ids), str(args.sandbox)))
  print 'Continue?'

  s = raw_input('(Y/N): ')
  if s == 'Y' or s == 'y':
    print 'Approving assignments'
    for idx, assignment_id in enumerate(approve_ids):
      print 'Approving assignment %d / %d' % (idx + 1, len(approve_ids))
      mtc.approve_assignment(assignment_id)
    for idx, assignment_id in enumerate(reject_ids):
      print 'Rejecting assignment %d / %d' % (idx + 1, len(reject_ids))
      mtc.reject_assignment(assignment_id, feedback='Invalid results')
  else:
    print 'Aborting'
