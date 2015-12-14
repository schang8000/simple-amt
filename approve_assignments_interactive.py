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
      if a.AssignmentStatus in ['Submitted', 'Approved', 'Rejected']:
        try:
          # Try to parse the output from the assignment. If it isn't
          # valid JSON then we reject the assignment.
          output = json.loads(a.answers[0][0].fields[0])
          print 'Approving assignment %s (%s), worker id: %s' % (a.AssignmentId, a.AssignmentStatus, a.WorkerId)
          s = raw_input('(A)pprove/(R)eject?')
          if s.lower() == 'a':
            if a.AssignmentStatus == 'Rejected':
              mtc.approve_rejected_assignment(a.AssignmentId, feedback='Reverted rejection')
            else:
              mtc.approve_assignment(a.AssignmentId)
          elif s.lower() == 'r':
            mtc.reject_assignment(a.AssignmentId, feedback='Invalid results')
        except ValueError as e:
          print "Invalid submission"
