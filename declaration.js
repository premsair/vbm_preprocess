const path = require('path');

module.exports = {
  users: [
    { username: 'jill', userData: { dirs: ['/home/brain/now/jilldata/mprage_5e_RMS_0003'], mat_path: '/home/brain/now/transform.mat', spm_path: '/home/brain/Downloads/spm12', out_path: '/home/brain/now/jilldata' } },
    { username: 'prem', userData: { dirs: ['/home/brain/now/premdata/mprage_5e_RMS_0003'], mat_path: '/home/brain/now/transform.mat', spm_path: '/home/brain/Downloads/spm12', out_path: '/home/brain/now/premdata' } },
    { username: 'sandeep', userData: { dirs: ['/home/brain/now/sandeepdata/mprage_5e_RMS_0003'], mat_path: '/home/brain/now/transform.mat', spm_path: '/home/brain/Downloads/spm12', out_path: '/home/brain/now/sandeepdata' } },
  ],
  server:{},
  computationPath: path.resolve(
    __dirname,
    './index.js'
  ),
  verbose: true,
};