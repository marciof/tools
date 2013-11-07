# (1) Install dependencies.
#     $ apt-get install -y tomcat7
#
# (2) Install Solr (version >= 4) by extracting the downloaded archive somewhere -- `$SOLR_INSTALL`. [1]
#
# (3) Create your own Solr Home directory -- `$SOLR_HOME`.
#     (1) Make a copy of the bundled example.
#         $ cp -r $SOLR_INSTALL/example/solr $SOLR_HOME
#     (2) Optionally change the default core name of "collection1" -- `$SOLR_CORE`.
#         $ $EDITOR $SOLR_HOME/solr.xml
#
# (4) Create a schema file for the Solr core.
#     $ $EDITOR $SOLR_HOME/$SOLR_CORE/conf/schema.xml
#
# (5) Create a configuration file for the Solr core.
#     (1) $ $EDITOR $SOLR_HOME/$SOLR_CORE/conf/schema.xml
#     (2) Correct `dir` (and `regex if needed) for clustering libraries by replacing `...` with `$SOLR_INSTALL`.
#         $ $EDITOR $SOLR_HOME/$SOLR_CORE/conf/solrconfig.xml
#         <lib dir=".../contrib/clustering/lib/" regex=".*\.jar" />
#         <lib dir=".../dist/" regex="solr-clustering-\d.*\.jar" />
#         Optionally change the default data directory in `<dataDir>` -- `$SOLR_DATA`.
#     (3) Enable the clustering component.
#         $ echo solr.clustering.enabled=true >> $SOLR_HOME/$SOLR_CORE/conf/solrcore.properties
#     (4) Correct the data directory's permissions for the `tomcat7` user.
#         $ chown tomcat7:tomcat7 $SOLR_DATA
#
# (6) If Solr is recent enough, it might need to have logging configured. [2]
#
# (7) Create a configuration file to run Solr within Tomcat, `$SOLR_CTX`. [3]
#     (1) Correct `docBase` to point where "solr.war" is.
#         $ find $SOLR_INSTALL -iname 'solr-*.war'
#     (2) Correct "solr/home" to point to `$SOLR_HOME`.
#     (3) Make this Solr instance/install known to Tomcat.
#         $ ln -s $SOLR_CTX /etc/tomcat7/Catalina/localhost/
#     (4) Re-/Start Tomcat.
#         $ service tomcat7 restart
#
# [1] http://lucene.apache.org/solr/
# [2] http://wiki.apache.org/solr/SolrLogging
# [3] http://wiki.apache.org/solr/SolrTomcat#Installing_Solr_instances_under_Tomcat
