from AMmodel.model import AM
from dataloaders.am_dataloader import AM_DataLoader
from utils.user_config import UserConfig
from tester import am_tester
import numpy as np
import argparse
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
class AM_Tester():
    def __init__(self,config):
        self.config=config['learning_config']

        self.am = AM(config)
        self.am.load_model(training=False)
        f,c=self.am.speech_feature.compute_feature_dim()
        self.am.model.return_pb_function(f,c)
        self.dg = AM_DataLoader(config,training=False)

        self.runner = am_tester.AMTester(self.config['running_config'],self.dg.text_featurizer)

        self.STT = self.am.model
        self.runner.set_progbar(self.dg.eval_per_epoch_steps())
        self.runner.compile(self.STT)
    def make_eval_batch_data(self):
        batches = []
        for _ in range(self.config['running_config']['eval_steps_per_batches']):
            features, wavs, input_length, labels, label_length = self.dg.eval_data_generator()
            input_length=np.expand_dims(input_length,-1)
            batches.append((features, wavs, input_length, labels, label_length))

        return batches

    def test(self):
        while 1:
            eval_batches=self.make_eval_batch_data()
            # print('now',self.dg.offset)
            self.runner.run(eval_batches)
            if self.dg.offset>len(self.dg.test_list)-1:
                break
if __name__ == '__main__':

    parse=argparse.ArgumentParser()
    parse.add_argument('--data_config',type=str,required=True,help='the am data config path')

    parse.add_argument('--model_config',type=str,required=True,help='the am model config path')
    args=parse.parse_args()

    config=UserConfig(args.data_config,args.model_config)
    test=AM_Tester(config)
    test.test()