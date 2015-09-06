from mrjob.job import MRJob
import mrjob
import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
import simplejson
import datetime


'''
HADOOP_HOME=/opt/cloudera/parcels/CDH/ python search-counts.py -r hadoop --output-dir data/searchCounts/fennec/ hdfs:///user/bcolloran/deorphaned/2014-07-07/v3small
'''

def utcStrToDate(utcStr):
    return datetime.date(int(utcStr[0:4]), int(utcStr[5:7]), int(utcStr[8:10]))

class getSearchCounts(MRJob):
    HADOOP_INPUT_FORMAT="org.apache.hadoop.mapred.SequenceFileAsTextInputFormat"
    INPUT_PROTOCOL = mrjob.protocol.RawProtocol
    OUTPUT_PROTOCOL = mrjob.protocol.RawProtocol
    INTERNAL_PROTOCOL = mrjob.protocol.JSONProtocol

    def mapper(self, key, rawJsonIn):
        self.increment_counter("MAPPER", "INPUT (docId,payload)")

        try:
            payload = simplejson.loads(rawJsonIn)
        except:
            self.increment_counter("MAP ERROR", "record failed to parse")
            self.increment_counter("MAP ERROR", "REJECTED RECORDS")
            return

        try:
            geoCountry = payload['geoCountry']
        except:
            geoCountry = "unknown"

        try:
            dataDays = payload['data']['days']
        except:
            self.increment_counter("MAP ERROR", "no dataDays")
            self.increment_counter("MAP ERROR", "REJECTED RECORDS")
            return

        try:
            for date, dateData in dataDays.items():
                if date >= "2014-06-01":
                    for env, envData in dateData.items():
                        searches = envData.get('org.mozilla.searches.count',{})
                        for sap, sapData in [tup for tup in searches.items() if tup[0] != "_v"]:
                            for provider, count in sapData.items():
                                print (geoCountry, sap, provider)
                                yield "%s|%s|%s"%(geoCountry, sap, provider), count
        except:
            self.increment_counter("MAP ERROR", "bad dataDays")
            self.increment_counter("MAP ERROR", "REJECTED RECORDS")
            return

    def combiner(self,key,countIter):
        try:
            yield key, sum(countIter)
        except:
            print >> sys.stderr, 'Exception (ignored)', sys.exc_info()[0], sys.exc_info()[1]
            print >> sys.stderr, "key",key,"countIter", str(countIter)
            self.increment_counter("combiner ERROR", "combiner failed")

    def reducer(self,key, countIter):
        yield key, str(sum(countIter))

if __name__ == '__main__':
    getSearchCounts.run()


