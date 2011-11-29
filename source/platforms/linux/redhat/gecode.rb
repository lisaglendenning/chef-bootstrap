#
# Modified gecode default.rb recipe from bootstrap cookbook v1.0
# November 28, 2011
# Installs gecode from RPM on centos/redhat to work around issue COOK-528
#

case node['platform']
when 'ubuntu','debian'

  include_recipe 'apt'

  # use opscode apt repo for older releases
  if (platform?("debian") && (node.platform_version.to_f < 7.0)) || 
      (platform?("ubuntu") && (node.platform_version.to_f < 11.0))

    # add Opscode's apt repo to sources
    apt_repository "opscode" do
      uri "http://apt.opscode.com"
      components ["main"]
      distribution node['lsb']['codename']
      key "2940ABA983EF826A"
      keyserver "pgpkeys.mit.edu"
      action :add
    end

  end

  apt_package 'libgecode-dev' do
    action :install
  end

when 'redhat','centos'

  package 'gecode-devel' do
    action :install
  end

else
  raise "This recipe does not yet support installing Gecode 3.5.0+ for your platform"
end
