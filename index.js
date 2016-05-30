'use strict';

module.exports = { // eslint-disable-line
  name: 'convert',
  version: '0.0.1',
  cwd: __dirname,
  local: {
    type: 'cmd',
    cmd: 'python',
    args: ['./vbm_preprocess_spm12.py'],
    verbose: true,
  },
  
  remote: {
    type: 'function',
    fn(opts, cb) {
      const data = opts.previousData || {};
      opts.userResults.forEach(rslt => (data[rslt.username] = rslt.data));
      if (data && Object.keys(data).length === opts.usernames.length) {
        data.complete = true;
      }
      console.error(data); // eslint-disable-line
      cb(null, data);
    },
    verbose: true,
  },
};